from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_advancement_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Контроль бюджета"), ],
            [KeyboardButton(text="Аналитика Рекламных Компаний"), ],
            [KeyboardButton(text="На главную", ), ],
        ]
    )
