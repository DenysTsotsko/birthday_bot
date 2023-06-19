from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

user_cb = CallbackData('id', 'name', 'action')


def get_menu_birthday() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('add', callback_data='add_birthday'),
         InlineKeyboardButton('delete', callback_data='delete_birthday')]
    ], row_width=2)
    return ikb

