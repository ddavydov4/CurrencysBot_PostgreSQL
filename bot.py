import logging
import os
import psycopg2 as pg
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    BotCommand, BotCommandScopeDefault

conn=pg.connect (user='postgres', password='postgres', host='localhost',port='5432', database='Currencys_Bot_PostgreSQL')
cursor=conn.cursor()

bot_token=os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=bot_token)
dp=Dispatcher(bot, storage=MemoryStorage())


button_save = KeyboardButton('/save_currency')
button_convert = KeyboardButton('/convert')
button_show = KeyboardButton('/get_currency')
button_delete = KeyboardButton('/delete_currency')
button_edit = KeyboardButton('/edit_currency')

buttons = ReplyKeyboardMarkup().add(button_save,button_delete, button_edit)

select_admins="Select * from admins"


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Действия отменены')


def get_id():
    df=cursor.execute("""Select chat_id from admins""")
    Admin_id = cursor.fetchall()

    Admin_id= re.sub(r"[^0-9]",r"",str(Admin_id))
    admins_list=[]
    if Admin_id in admins_list:
        return (admins_list)
    else:
        admins_list.append(Admin_id)
        return (admins_list)

def add_currencies(currencies):
    cursor.execute(""" Insert into currencies (currency_name, rate) 
        values (%s,%s);""",currencies)
    conn.commit()
    currencies.clear()


class Form(StatesGroup):
    name = State()
    delete_name = State()
    edit_name = State()
    edit_name1 = State()
    rate = State()
    check = State()
    num = State()
    delete = State()
    save1 = State()
    save2 = State()
    save3 = State()


currencies=[]
f_name=[]

user_comands = [
    BotCommand(command='/start', description='start'),
    BotCommand(command='/convert', description='Конвертировать'),
    BotCommand(command='/get_currency', description='Показать валюты'),
    BotCommand(command='/id', description='let id')
]
admin_commands = [
    BotCommand(command='/start', description='start'),
    BotCommand(command='/manage_currency', description='Менеджер валют'),
    BotCommand(command='/convert', description='Конвертировать'),
    BotCommand(command='/get_currency', description='Показать валюты'),
    BotCommand(command='/save_currency', description='Добавить валюту'),
    BotCommand(command='/edit_currency', description='Редактировать валюту')
]



#функции команд
@dp.message_handler(commands=['id'])
async def let_id(message: types.Message):
    await message.answer(message.chat.id)


@dp.message_handler(commands=['start'])
async def start_comand(message: types.Message):
    await bot.set_my_commands(user_comands,
scope=BotCommandScopeDefault())
    await message.reply("Привет! Здесь вы можете сделать перевод валюты.")


@dp.message_handler(commands=['manage_currency'])
async def manage_comand(message: types.Message):
    admin_id=get_id()
    admin = str(message.chat.id)
    await bot.set_my_commands(user_comands,
    scope=BotCommandScopeDefault())
    if admin in admin_id:
        await bot.set_my_commands(admin_commands,scope=BotCommandScopeDefault(chat_id=admin))
        await message.reply("Вы админ",reply_markup=buttons)
    else:
        await message.reply("Нет доступа к команде")

@dp.message_handler(commands=['save_currency'])
async def save_comand(message: types.Message):
    admin_id = get_id()
    admin = str(message.chat.id)
    if admin in admin_id:
        await message.reply("Введите название валюты")
        await Form.save2.set()
    else:
        await message.reply("Нет доступа к команде")


@dp.message_handler(state=Form.save2)
async def process_save2(message: types.Message, state: FSMContext):
    name =message.text
    curr = cursor.execute("""Select currency_name from currencies where 
currency_name=%s""",(name,))
    curr = cursor.fetchall()

    if curr==[]:
        currencies.append(name)
        await message.reply("Введите курс валюты")
        await Form.save3.set()
    else:
        await message.reply("Валюта уже существует")

@dp.message_handler(state=Form.save3)
async def process_save3(message: types.Message, state: FSMContext):
    rate = message.text
    currencies.append(rate)
    add_currencies(currencies)
    await message.reply("Сохранено")
    await state.finish()


@dp.message_handler(commands=['get_currency'])
async def convert_comand(message: types.Message):
    curr = cursor.execute("""Select currency_name, rate from currencies""")
    curr = cursor.fetchall()
    await message.reply(curr)

@dp.message_handler(commands=['delete_currency'])
async def delete_comand(message: types.Message):
    admin_id = get_id()
    admin = str(message.chat.id)
    if admin in admin_id:
        await Form.delete_name.set()
        await message.reply("Введите название валюты")
    else:
        await message.reply("Нет доступа к команде")

@dp.message_handler(state=Form.delete_name)
async def process_delete(message: types.Message, state: FSMContext):
    name = message.text
    cursor.execute("""delete from currencies where currency_name=%s""", (name,))
    conn.commit()
    await message.reply('Удалено')
    await state.finish()


@dp.message_handler(commands=['edit_currency'])
async def edit_comand(message: types.Message):
    admin_id = get_id()
    admin = str(message.chat.id)
    if admin in admin_id:
        await Form.edit_name.set()
        await message.reply("Введите название валюты")
    else:
        await message.reply("Нет доступа к команде")

@dp.message_handler(state=Form.edit_name)
async def process_rate(message: types.Message, state: FSMContext):
    name = message.text
    f_name.append(name)
    await Form.edit_name1.set()
    await message.reply('Введите курс к рублю')


@dp.message_handler(state=Form.edit_name1)
async def process_rate1(message: types.Message, state: FSMContext):
    rate = message.text
    cursor.execute("""UPDATE currencies SET rate=%s WHERE 
currency_name=%s""", (rate,f_name[0],))
    conn.commit()
    await message.reply('Сохранено')
    f_name.clear()
    await state.finish()


@dp.message_handler(commands=['convert'])
async def convert_comand(message: types.Message):
    await Form.check.set()
    await message.reply("Введите название валюты")

@dp.message_handler(state=Form.check)
async def process_check(message: types.Message, state: FSMContext):
    await state.update_data(cheack_rate=message.text)
    name = message.text
    curr = cursor.execute("""Select rate from currencies where lower 
(currency_name)=lower (%s)""", (name,))
    curr = str(cursor.fetchall())
    curr = re.sub(r"[^0-9,]",r"",curr)
    curr = float(re.sub(r"[,]", r".", curr))
    f_name.append(curr)
    await Form.num.set()
    await message.reply("Введите сумму перевода")


@dp.message_handler(state=Form.num)
async def process_convert(message: types.Message, state: FSMContext):
    num = message.text
    result = float(f_name[0]) * float(num)
    await message.reply(result)
    f_name.clear()
    await state.finish()

#точка входа в приложение
if __name__ =='__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)