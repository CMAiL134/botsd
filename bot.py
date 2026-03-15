import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from channels import CHANNELS

TOKEN = "8405203601:AAHbFIJJwcAjcIZaVe2uXpSVTBjppClBAmc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# хранение последних сообщений
last_messages = {}

# автоматическая загрузка файлов
PROGRAMS = {}

for file in os.listdir("files"):
    name = file.split(".")[0]
    PROGRAMS[name] = f"files/{file}"


async def delete_last(chat_id, user_id):

    if user_id in last_messages:
        try:
            await bot.delete_message(chat_id, last_messages[user_id])
        except:
            pass


async def save_message(user_id, message_id):

    last_messages[user_id] = message_id


async def check_subscriptions(user_id):

    for channel in CHANNELS:

        member = await bot.get_chat_member(channel["id"], user_id)

        if member.status in ["left", "kicked"]:
            return channel

    return None


@dp.message(Command("start"))
async def start(message: types.Message):

    user_id = message.from_user.id

    not_subscribed = await check_subscriptions(user_id)

    if not_subscribed:

        msg = await message.answer(
            f"Для того чтоб начать пользоваться ботом подпишись на канал:\n{not_subscribed['link']}"
        )

        await save_message(user_id, msg.message_id)
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Получить программу")]],
        resize_keyboard=True
    )

    msg = await message.answer(
        "Нажмите кнопку чтобы получить программу",
        reply_markup=keyboard
    )

    await save_message(user_id, msg.message_id)


@dp.message(lambda message: message.text == "Получить программу")
async def choose_program(message: types.Message):

    user_id = message.from_user.id

    await delete_last(message.chat.id, user_id)

    buttons = [[KeyboardButton(text=name)] for name in PROGRAMS]

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    msg = await message.answer(
        "Выберите программу:",
        reply_markup=keyboard
    )

    await save_message(user_id, msg.message_id)


@dp.message()
async def send_program(message: types.Message):

    user_id = message.from_user.id

    not_subscribed = await check_subscriptions(user_id)

    if not_subscribed:

        msg = await message.answer(
            f"Для того чтоб начать пользоваться ботом подпишись на канал:\n{not_subscribed['link']}"
        )

        await save_message(user_id, msg.message_id)
        return

    if message.text in PROGRAMS:

        await delete_last(message.chat.id, user_id)

        msg = await message.answer_document(
            types.FSInputFile(PROGRAMS[message.text])
        )

        await save_message(user_id, msg.message_id)

        promo = await message.answer(
            "А если хочешь индивидуальную программу, со всеми корректировками лично под тебя "
            "то можешь ознакомиться со всеми ПРАЙСАМИ тут:\n@wedeni_skeleTT"
        )

        await save_message(user_id, promo.message_id)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
