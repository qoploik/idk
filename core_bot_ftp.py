import os
from dotenv import load_dotenv
load_dotenv()  # loads .env file if it exists

FREECURRENCY_API_KEY = os.environ["FREECURRENCY_API_KEY"]
TOKEN = os.environ["TG_BOT_TOKEN"]

import json
import re
#import requests
import asyncio
from db import init_db
from db import log_request
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
import freecurrencyapi

with open("exchange_rates.json", "r", encoding="utf-8") as f:
    filtered_curr = json.load(f)

#client = freecurrencyapi.Client(FREECURRENCY_API_KEY)
#EUR_curr = client.latest(base_currency='EUR')
#SET_curr = ['USD', 'RUB']
#filtered_curr = {k: v for k, v in EUR_curr['data'].items() if k in SET_curr}

min_com = 1.1
max_com = 1.3
min_value = 30
usdt_prem = 1.05

# Bot initialization (aiogram 3.7+)
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

#МОЯ ПОЛНОСТЬЮ КОМАНДА
@dp.message(Command("get_price"))
async def get_price(message: Message):
    await message.answer(
        "Если вы уже нашли нужный вам товар и хотите узнать его конечную стоимость в RUB или USDT - укажите его стоимость:\n"
        "15.95\n"
        "Если товаров больше одного - вводите цены по порядку:\n"
        "15 - 99.90 - 299.9"
    )

# --- /start COMMAND ---
@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup( #!!!
        inline_keyboard=[
            [InlineKeyboardButton(text="узнать цены🔮", callback_data="get_price")],
            [InlineKeyboardButton(text="Связь", url="https://t.me/lil_georgii")],
            [InlineKeyboardButton(text="faq", callback_data="faq")]
        ]
    )
    await message.answer(
        "Здесь вы можете узнать конечные цены на планируемые к заказу <i>items</i>✨!\n"
        "Как при возникновении вопросов, так и для заказа - пишите менеджеру. Ваш байер!❤️\n",
        reply_markup=keyboard)

# --- /faq COMMAND ---
@dp.message(Command("faq"))
async def faq_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="узнать цены🔮", callback_data="get_price")],
            [InlineKeyboardButton(text="админ паблика", url="https://t.me/lil_georgii")]
        ]
    )
    await message.answer(
        "<b>Частые вопросы:...</b> и ответы к ним!\n"
        "<b>1. Откуда ограничение на 300💶?</b>\n"
        "Это условные порог, после которого у таможни могут быть вопросы. Так как данный порог условный - в любом случае лучше уточнить у менеджера возможность отправке\n"
        "<b>2. Как устроено ценообразование?</b>\n"
        "Мы за прозрачный и понятный подход. У сервиса есть минимальная комиссия в 30 EUR на покупки, которая уменьшается до 10% с увеличением общего чека для более выгодных покупок :)\n" 
        "<b>3. Вы делаете оффлайн выкупы, поход на распродажи?</b>\n"
        "За деньги да (в Германии)", reply_markup=keyboard)

# --- /contact COMMAND ---
@dp.message(Command("contact"))
async def contact_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="админ паблика", url="https://t.me/lil_georgii")],
            [InlineKeyboardButton(text="посчитать стоимость🔮", callback_data="get_price")],
            [InlineKeyboardButton(text="вопросы и ответы", callback_data="faq")]
        ]
    )
    await message.answer("<b>связаться⬇️</b>", reply_markup=keyboard)


# --- CALLBACK BUTTONS HANDLER ---
@dp.callback_query(F.data.in_({"start", "get_price", "faq", "contact"}))
async def callback_handler(callback: CallbackQuery):
    if callback.data == "start":
        await start_handler(callback.message)
    elif callback.data == "get_price":
        await get_price(callback.message)
    elif callback.data == "faq":
        await faq_handler(callback.message)
    elif callback.data == "contact":
        await contact_handler(callback.message)
    await callback.answer()


# --- USER INPUT HANDLER ---
@dp.message()
async def user_input_handler(message: Message):
    raw_string = message.text
    try:
        index = parse_index(raw_string)
        await log_request(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            raw_entry=message.text,
            index_array=index,  # your parsed float list
        )
        if not index:
            await existence_error(message)
            return
        if any(value > 300 for value in index):
            await exceed_value(message)
            return
        else:
            await calculate_price(message, index)
    except ValueError:
        await existence_error(message)
        

def parse_index(raw_string: str) -> list[float]:
    """ Extracts float values from a messy input string:
    - Replaces commas with dots for decimals
    - Replaces all non-numeric/non-dot characters with space
    - Returns a list of float numbers """
    cleaned = re.sub(r"[^0-9.\s]", " ", raw_string.replace(",", "."))
    return [float(x) for x in cleaned.split() if x.strip()]

# --- SHARED REPLY KEYBOARD FOR ERRORS ---
def error_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Рассчитать снова", callback_data="start")],
            [InlineKeyboardButton(text="Связь", callback_data="contact")]
        ]
    )

async def existence_error(message: Message):
    await message.answer("Вводите цифры :)", reply_markup=error_keyboard())
async def exceed_value(message: Message):
    await message.answer("Одно из значений превышает 300 EUR - напишите менеджеру", reply_markup=error_keyboard())
async def calculate_price(message: Message, index: list[float]):
    XXX = sum(index)
    if XXX <= 100:
        TOTAL = XXX + min_value
    elif XXX > 1000:
        TOTAL = XXX * min_com
    else:
        coeff = min_value + ((XXX - 100) * (100 - min_value)) / (1000 - 100)
        TOTAL = XXX + coeff
    real_com = TOTAL - XXX
    rubles = "{:,.1f}".format(TOTAL * filtered_curr['RUB']).replace(",", " ")
    usdt = "{:,.1f}".format(TOTAL * filtered_curr['USD'] * usdt_prem).replace(",", " ")
    SUM_USD = sum(index)*filtered_curr['USD']
    SUM_RUB = sum(index)*filtered_curr['RUB']
    await message.answer(f"Стоимость вашей покупки составит {sum(index):.2f} EUR,"
                         f" с учетом комиссии сервиса (+доставка) {real_com:.2f} EUR составит {TOTAL:.2f} EUR.\n"
                         f"При оплате в рублях будет <i>{rubles} руб.</i>.\n"
                         f"При оплате в USDT выйдет <i>{usdt} USD</i>")

#уб.</i>,\nПри оплате в USDT выйдет <i>{usdt} USD</i>"

# --- MAIN ENTRYPOINT ---
async def main():
    await init_db()       # creates tables if they don't exist
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())