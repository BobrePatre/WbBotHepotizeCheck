from aiogram import Router, filters, types, Dispatcher, Bot, F
from aiogram.client import bot
from aiogram.fsm.context import FSMContext

import keyboards.warehouse

from states.warehouse import AddArticle, AddProducment, ChangingLimit, ChangingLowerLimit, ItemsInfo, DeleteArticle
from repository.mongo.warehouse import WarehouseRepository


class Warehouse:
    def __init__(self, bot: Bot, dp: Dispatcher, warehouse_repo: WarehouseRepository):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="warehouse")
        self.warehouse_repo = warehouse_repo

    async def menu(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(
            message.from_user.id,
            "Опции по складу",
            reply_markup=keyboards.warehouse.get_warehouse_menu()
        )

    # Article zone
    async def start_input_article(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(message.from_user.id, "Введите артикул продавца для отслеживания")
        await state.set_state(state=AddArticle.article)

    async def input_article(self, message: types.Message, state: FSMContext):
        await state.update_data({
            "article": message.text
        })
        await self.bot.send_message(message.from_user.id, "Записал! Введите название товара")
        await state.set_state(state=AddArticle.name)

    async def input_article_name(self, message: types.Message, state: FSMContext):
        await state.update_data({
            "name": message.text
        })
        await self.bot.send_message(message.from_user.id, "Принял! Теперь введите текущий остаток по данному товару")
        await state.set_state(state=AddArticle.limit)

    async def input_article_limit(self, message: types.Message, state: FSMContext):
        await state.update_data({
            "limit": int(message.text)
        })
        await self.bot.send_message(message.from_user.id, "Супер! Введите допустимый остаток на складе (Число товара, "
                                                          "которое должно быть на складе. Если товара станет меньше "
                                                          "заданного значения - бот вышлет Вам уведомление)")
        await state.set_state(state=AddArticle.lower_limit)

    async def input_article_lower_limit(self, message: types.Message, state: FSMContext):
        await state.update_data({
            "lower_limit": int(message.text)
        })

        data = await state.get_data()
        print(data)
        await self.bot.send_message(
            message.from_user.id,
            f"Готово!\n"
            f"```text\n"
            f"Артикул - {data['article']}\n"
            f"Товар - {data['name']}\n"
            f"Остаток товара на складе - {data['limit']}\n"
            f"Лимит по остатку - {data['lower_limit']}\n```"
            f"Все верно?",
            reply_markup=keyboards.warehouse.get_confirm_kb(),
            parse_mode="markdown"
        )
        await state.set_state(state=AddArticle.confirm_data)

    async def input_article_confirm(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        await state.set_state(state=None)
        if callback.data == "agree":
            self.warehouse_repo.add_new_article_to_user(callback.from_user.id, {
                "article": data["article"],
                "limit": data["limit"],
                "lower_limit": data["lower_limit"],
                "name": data["name"],
            })
            await self.bot.send_message(callback.from_user.id, "Товар успешно сохранен!")
            return
        await self.bot.send_message(callback.from_user.id, "Начнем заново! Введи артикул:")
        await state.set_state(state=AddArticle.article)

    # End Article zone

    # procurement zone

    async def start_adding_procurement(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(
            message.from_user.id,
            "Выберите товар для внесения закупки:",
            reply_markup=keyboards.warehouse.generate_articles_inline_list(
                self.warehouse_repo.get_users_articles(message.from_user.id))
        )
        await state.set_state(state=AddProducment.article)

    async def choose_article_producrement(self, callback: types.CallbackQuery, state: FSMContext):
        await state.update_data({
            "article": callback.data
        })
        await self.bot.send_message(callback.from_user.id, "Введите количество заказанного товара")
        await state.set_state(state=AddProducment.productment)

    async def input_productment(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        article_from_db = self.warehouse_repo.get_article(data["article"])["article"]
        article_from_db["limit"] = article_from_db["limit"] + int(message.text)
        self.warehouse_repo.set_new_limit(data['article'], article_from_db["limit"])
        await self.bot.send_message(message.from_user.id, f"Принял!"
                                                          f" Текущий остаток по товару {article_from_db['name']}: "
                                                          f"{article_from_db['limit']}")
        await state.set_state(state=None)

    # end productment zone

    # limit zone 
    async def start_limit_changing(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(
            message.from_user.id,
            "Выберите товар для изменения остатков",
            reply_markup=keyboards.warehouse.generate_articles_inline_list(
                self.warehouse_repo.get_users_articles(message.from_user.id))
        )
        await state.set_state(state=ChangingLimit.article)

    async def choose_article_limit(self, callback: types.CallbackQuery, state: FSMContext):
        await state.update_data({
            "article": callback.data
        })
        await self.bot.send_message(callback.from_user.id, "Введите реальный остаток на складе"
                                                           " (учитывая все идущие поставки):")
        await state.set_state(state=ChangingLimit.new_limit)

    async def input_limit(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        article_from_db = self.warehouse_repo.get_article(data["article"])["article"]
        article_from_db["limit"] = int(message.text)
        print(article_from_db['limit'])
        self.warehouse_repo.set_new_limit(data['article'], article_from_db["limit"])
        await self.bot.send_message(message.from_user.id,
                                    f"Принял! Текущий остаток по товару {article_from_db['name']} - {article_from_db['limit']}")
        await state.set_state(state=None)

    # end limit zone

    # lower limit zone
    async def start_lower_limit_changing(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(
            message.from_user.id,
            "Выберите товар для изменения минимальных остатков",
            reply_markup=keyboards.warehouse.generate_articles_inline_list(
                self.warehouse_repo.get_users_articles(message.from_user.id))
        )
        await state.set_state(state=ChangingLowerLimit.article)

    async def choose_lower_article_limit(self, callback: types.CallbackQuery, state: FSMContext):
        await state.update_data({
            "article": callback.data
        })
        await self.bot.send_message(callback.from_user.id, "Введите минимальный остаток на складе")
        await state.set_state(state=ChangingLowerLimit.new_limit)

    async def input_lower_limit(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        article_from_db = self.warehouse_repo.get_article(data["article"])["article"]
        article_from_db["lower_limit"] = int(message.text)
        self.warehouse_repo.set_new_lower_limit(data['article'], article_from_db["lower_limit"])
        await self.bot.send_message(message.from_user.id,
                                    f"Принял! Минимальный остаток по товару {article_from_db['name']} - {article_from_db['lower_limit']}")
        await state.set_state(state=None)

    # end lower limit zone

    # items info zone
    async def show_items_list(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(message.from_user.id, "Ваши товары:",
                                    reply_markup=keyboards.warehouse.generate_articles_inline_list(
                                        self.warehouse_repo.get_users_articles(message.from_user.id)))
        await state.set_state(ItemsInfo.article)

    async def show_item_info(self, callback: types.CallbackQuery, state: FSMContext):
        item = self.warehouse_repo.get_article(callback.data)["article"]
        await self.bot.send_message(
            callback.from_user.id,
            f"```text\n"
            f"Товар - {item['name']}\n"
            f"Артикул - {item['article']}\n"
            f"Остаток - {item['limit']}\n"
            f"Минимальный остаток - {item['lower_limit']}```",
            parse_mode="markdown"
        )

        await state.set_state(None)

    # end items info zone

    # deleting article zone

    async def start_deleting(self, message: types.Message, state: FSMContext):
        articles = self.warehouse_repo.get_users_articles(message.from_user.id)
        await self.bot.send_message(
            message.from_user.id,
            "Выберите артикул, который вы хотите удалить:",
            reply_markup=keyboards.warehouse.generate_articles_inline_list(articles)
        )
        await state.set_state(state=DeleteArticle.article)

    async def delete_article(self, callback: types.CallbackQuery, state: FSMContext):
        self.warehouse_repo.delete_article(callback.data)
        await self.bot.send_message(callback.from_user.id, f"Артикул - {callback.data} удален!")
        await state.set_state(None)

    # end deleting article zone

    # start all stocks

    async def show_all_stocks(self, message: types.Message):
        articles = self.warehouse_repo.get_users_articles(message.from_user.id)
        msg = ""
        for article in articles:
            art = article["article"]
            msg += f"{art["name"]} ({art['article']}) - {art["limit"]}шт.\n"
        await self.bot.send_message(message.from_user.id, "Ваши текущие остатки: \n" + msg)

    # end all stocks

    # Register Zone
    def register_handlers(self):
        self.router.message.register(self.show_all_stocks, F.text == "Все остатки")

        # -------
        self.router.message.register(self.start_deleting, F.text == "Удалить артикул")
        self.router.callback_query.register(self.delete_article, filters.StateFilter(DeleteArticle.article))

        # -------
        self.router.message.register(self.show_items_list, F.text == "Посмотреть остатки")
        self.router.callback_query.register(self.show_item_info, filters.StateFilter(ItemsInfo.article))

        # -------
        self.router.message.register(self.start_lower_limit_changing, F.text == "Изменить минимальный остаток")
        self.router.callback_query.register(self.choose_lower_article_limit,
                                            filters.StateFilter(ChangingLowerLimit.article))
        self.router.message.register(self.input_lower_limit, filters.StateFilter(ChangingLowerLimit.new_limit))

        # -------
        self.router.message.register(self.start_limit_changing, F.text == "Изменить текущий остаток на складе")
        self.router.callback_query.register(self.choose_article_limit, filters.StateFilter(ChangingLimit.article))
        self.router.message.register(self.input_limit, filters.StateFilter(ChangingLimit.new_limit))

        # -------
        self.router.message.register(self.start_adding_procurement, F.text == "Внести закупку")
        self.router.callback_query.register(self.choose_article_producrement,
                                            filters.StateFilter(AddProducment.article))
        self.router.message.register(self.input_productment, filters.StateFilter(AddProducment.productment))

        # -------
        self.router.message.register(self.start_input_article, F.text == "Добавить артикул для отслеживания")
        self.router.message.register(self.input_article, filters.StateFilter(AddArticle.article))
        self.router.message.register(self.input_article_name, filters.StateFilter(AddArticle.name))
        self.router.message.register(self.input_article_limit, filters.StateFilter(AddArticle.limit))
        self.router.message.register(self.input_article_lower_limit, filters.StateFilter(AddArticle.lower_limit))

        # --------
        self.router.callback_query.register(self.input_article_confirm, filters.StateFilter(AddArticle.confirm_data))
        self.router.message.register(self.menu, F.text == "Склад")
        self.dp.include_router(self.router)
