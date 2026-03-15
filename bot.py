import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from channels import CHANNELS

TOKEN = "8405203601:AAHbFIJJwcAjcIZaVe2uXpSVTBjppClBAmc"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Автоматическое считывание файлов из папки
PROGRAMS = {}
for file in os.listdir("files"):
    if file.endswith(".xlsx"):
        name = file.replace(".xlsx", "")
        PROGRAMS[name] = f"files/{file}"

# Проверка подписки
async def check_subscriptions(user_id):
    not_subscribed = []
    for channel in CHANNELS:
        member = await bot.get_chat_member(channel["id"], user_id)
        if member.status in ["left", "kicked"]:
            not_subscribed.append(channel)
    return not_subscribed

# Кнопки подписки
def subscription_keyboard(channels):
    buttons = [[InlineKeyboardButton(text="Подписаться", url=ch["link"])] for ch in channels]
    buttons.append([InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subs")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    not_subscribed = await check_subscriptions(user_id)
    if not_subscribed:
        await message.answer("Чтобы пользоваться ботом, подпишитесь на каналы:", reply_markup=subscription_keyboard(not_subscribed))
        return
    await message.answer("✅ Вы подписаны. Нажмите кнопку ниже.", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Получить программу")]],
        resize_keyboard=True
    ))

# Кнопка "Я подписался"
@dp.callback_query(lambda c: c.data == "check_subs")
async def check_again(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_subscribed = await check_subscriptions(user_id)
    if not_subscribed:
        await callback.message.edit_text("❌ Вы подписались не на все каналы", reply_markup=subscription_keyboard(not_subscribed))
    else:
        await callback.message.edit_text("✅ Подписка подтверждена!")
        await callback.message.answer("Теперь можно пользоваться ботом.", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Получить программу")]],
            resize_keyboard=True
        ))

# Кнопка "Получить программу"
@dp.message(lambda message: message.text == "Получить программу")
async def choose_program(message: types.Message):
    buttons = [[KeyboardButton(text=name)] for name in PROGRAMS]
    await message.answer("Выберите программу:", reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))

# Отправка выбранной программы
@dp.message()
async def send_program(message: types.Message):
    if message.text in PROGRAMS:
        await message.answer_document(types.FSInputFile(PROGRAMS[message.text]))

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())