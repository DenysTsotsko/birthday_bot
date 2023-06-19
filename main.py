import sqlite3
import time
from random import randrange

from aiogram import Bot, executor, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import exceptions
from aiogram.utils.markdown import bold

import datetime
import asyncio
import schedule
import aiosqlite


import sqlite_db
from text import HELP_COMMAND, LIST_STICKERS, LIST_STICKERS_SAD
from config import TOKEN_API
from keyboads import get_menu_birthday

storage = MemoryStorage()
bot = Bot(token=TOKEN_API,
          parse_mode="HTML")
dp = Dispatcher(bot,
                storage=storage)


class ProfileStatesGroup(StatesGroup):
    chat_id = State()
    user_name = State()
    dates = State()
    user_name_delete = State()


async def on_startup(_):
    await sqlite_db.db_start()
    print("Connected to bd")


@dp.message_handler(commands=['start'])
async def send_hello(message: types.Message):
    await message.reply(text="Добро пожаловать\nЧтобы узнать больше напишите /help")


@dp.message_handler(commands=['help'])
async def send_list(message: types.Message):
    await message.answer(text=HELP_COMMAND,
                         parse_mode='HTML')


@dp.message_handler(commands=['menu'])
async def send_menu(message: types.Message):
    await message.answer(text='Выберите кнопку ниже и следуйте инструкции\n\nadd - добавить дату\ndelete - удалить дату',
                         reply_markup=get_menu_birthday())



@dp.message_handler(commands=['stop'], state=[ProfileStatesGroup.user_name, ProfileStatesGroup.dates])
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply('Создание даты дня рождения было прервано')


@dp.message_handler(commands=['stop'], state=[ProfileStatesGroup.user_name_delete])
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply('Профиль не был удален')


@dp.callback_query_handler(text='add_birthday')
async def add_user(callback: types.CallbackQuery) -> None:
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    global msg_name
    msg_name = await callback.message.answer('Введите имя пользователя оно должно начинаться с @\n/stop - выйти')
    await ProfileStatesGroup.user_name.set()


@dp.message_handler(lambda message: not "@" in message.text,
                    state=ProfileStatesGroup.user_name)
async def check_date(message: types.Message):
    msg_name_check = await message.reply('Пожалуйста повторите попытку, имя пользователя должно начинаться с @')
    await asyncio.sleep(5)
    await msg_name_check.delete()


@dp.message_handler(state=ProfileStatesGroup.user_name)
async def load_user_name(message: types.Message, state: FSMContext) -> None:
    global msg_date
    async with state.proxy() as data:
        data['user_name'] = message.text
        await msg_name.delete()
    msg_date = await message.answer('Сейчас напишите month/day. Например: 01/31\n/stop - выйти')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: not "/" in message.text and int(message.text[0:2]) in [0,1,2,3,4,5,6,7,8,9,10,11,12],
                    state=ProfileStatesGroup.dates)
async def check_date(message: types.Message):
    msg_date_check = await message.reply('Пожалуйста введите за таким принципом --> month/day')
    await asyncio.sleep(5)
    await msg_date_check.delete()


@dp.message_handler(state=[ProfileStatesGroup.dates, ProfileStatesGroup.chat_id])
async def make_date(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['chat_id'] = message.chat.id
        data['dates'] = message.text
    await bot.send_message(chat_id=message.chat.id,
                           text=f"🎁 Дата дня рождения 🎁\n<b>Имя:</b> {data['user_name']}\n<b>Дата дня рождения:</b> {data['dates']}",
                           parse_mode='HTML')
    await msg_date.delete()
    await sqlite_db.create_profile(state)
    await state.finish()


@dp.callback_query_handler(text='delete_birthday')
async def delete_product_cb(callback: types.CallbackQuery) -> None:
    global msg_dlt
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await ProfileStatesGroup.user_name_delete.set()
    msg_dlt = await callback.message.answer('Чтобы удалить дату, напишите @"имя пользователя"\n/stop - остановить удаление ')


@dp.message_handler(state=ProfileStatesGroup.user_name_delete)
async def delete_birtday_state(message: types.Message, state: FSMContext) -> None:
    id_ch = message.chat.id
    async with state.proxy() as data:
        data['user_name'] = message.text
    async with aiosqlite.connect('server.db') as db:
        async with db.execute("SELECT user_name FROM users WHERE user_name = ?", (data['user_name'],)) as cursor:
            rows = await cursor.fetchall()
            if len(rows) == 0:
                await bot.send_message(id_ch, f"Не удалось найти пользователя с именем '{message.text}', попробуйте еще раз")
            else:
                await sqlite_db.delete_birthday(data['user_name'])
                await message.reply(f'Пользователь "{message.text}" был удален')
    await msg_dlt.delete()
    await state.finish()


@dp.message_handler(commands=["today"])
async def send_message_for_today(message: types.Message):
    id_ch = message.chat.id
    async with aiosqlite.connect('server.db') as db:
        today = datetime.datetime.now().strftime("%m/%d")
        no_month = datetime.datetime.now().strftime("%m")
        no_day = datetime.datetime.now().strftime("%d")
        async with db.execute("SELECT chat_id, user_name FROM users WHERE dates = ?", (today,)) as cursor:
            rows = await cursor.fetchall()
            if len(rows) == 0:
                async with db.execute("SELECT chat_id, user_name FROM users WHERE dates = ?", (no_month,)) as cursorr:
                    rowss = await  cursorr.fetchall()
                await bot.send_message(id_ch, "Сегодня нету именинника, пробуйте завтра!")
                await bot.send_sticker(id_ch, LIST_STICKERS_SAD[randrange(1, 6)])
            else:
                for row in rows:
                    chat_id, user_name = row
                    if chat_id == id_ch:
                        message_text = f"🎁 Сегодня день рождения у {user_name}! 🎁"
                        try:
                            await bot.send_message(chat_id, message_text)
                            await bot.send_sticker(chat_id, LIST_STICKERS[randrange(1, 13)])
                        except exceptions.BotBlocked:
                            print(f" {chat_id} блок бота")
                        except exceptions.ChatNotFound:
                            print(f"Чат {chat_id} не найден")



if __name__ == "__main__":
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)