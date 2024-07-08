from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_warehouse_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить артикул для отслеживания"), ],
            [KeyboardButton(text="Внести закупку"), ],
            [KeyboardButton(text="Изменить текущий остаток на складе"), ],
            [KeyboardButton(text="Изменить минимальный остаток"), ],
            [KeyboardButton(text="Посмотреть остатки"), ],
            [KeyboardButton(text="Все остатки"), ],
            [KeyboardButton(text="Удалить артикул", ), ],
            [KeyboardButton(text="На главную", ), ],
        ]
    )


def get_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="agree"), ],
            [InlineKeyboardButton(text="Нет", callback_data="disagree"), ]
        ]
    )


def generate_articles_inline_list(articles: list[dict[str, any]]) -> InlineKeyboardMarkup:
    buttons = []
    for article in articles:
        print(article)
        buttons.append(
            [InlineKeyboardButton(text=article['article']['name'], callback_data=f"{article['article']['article']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
