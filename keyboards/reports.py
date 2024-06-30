from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder


def get_report_type_choise():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Чат с ботом", callback_data="chat_bot"), ],
            [InlineKeyboardButton(text="Excel", callback_data="excel"), ]
        ]
    )
