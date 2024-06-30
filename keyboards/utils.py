from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_url_button(title, url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title, url=url)],
    ])
