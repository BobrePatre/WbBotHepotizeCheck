from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать 👋"), ],
        ]
    )


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Склад"), ],
            [KeyboardButton(text="Продвижение"), ],
            [KeyboardButton(text="Сводная аналитика"), ],
            [KeyboardButton(text="Отчеты"), ],
            [KeyboardButton(text="Оцифровка показателей"), ],

        ]
    )
