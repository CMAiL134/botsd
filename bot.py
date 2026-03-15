import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from channels import CHANNELS

TOKEN = "8405203601:AAHbFIJJwcAjcIZaVe2uXpSVTBjppClBAmc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

BASE_DIR = "files"

# хранение сообщений программ
user_program_message = {}


# проверка подписки
async def check_subscriptions(user_id):

    for channel in CHANNELS:

        member = await bot.get_chat_member(channel["id"], user_id)

        if member.status in ["left", "kicked"]:
            return channel

    return None


# меню категорий
def categories_menu():

    buttons = []

    for folder in os.listdir(BASE_DIR):

        if os.path.isdir(f"{BASE_DIR}/{folder}"):

            buttons.append([
                InlineKeyboardButton(
                    text=folder,
                    callback_data=f"cat_{folder}"
                )
            ])

    buttons.append([
        InlineKeyboardButton(
            text="❤️ ПОДДЕРЖАТЬ АВТОРА",
            callback_data="support"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# меню программ
def programs_menu(category):

    buttons = []

    path = f"{BASE_DIR}/{category}"

    for file in os.listdir(path):

        name = file.split(".")[0]

        buttons.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"prog_{category}|{file}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="back"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# старт
@dp.message(Command("start"))
async def start(message: types.Message):

    user_id = message.from_user.id

    not_subscribed = await check_subscriptions(user_id)

    if not_subscribed:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Подписаться",
                    url=not_subscribed["link"]
                )],
                [InlineKeyboardButton(
                    text="Проверить подписку",
                    callback_data="check_sub"
                )]
            ]
        )

        await message.answer(
            "Для того чтоб начать пользоваться ботом подпишись на канал",
            reply_markup=keyboard
        )
        return

    await message.answer(
        "Выберите категорию программ:",
        reply_markup=categories_menu()
    )


# проверка подписки
@dp.callback_query(lambda c: c.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):

    user_id = callback.from_user.id

    not_subscribed = await check_subscriptions(user_id)

    if not_subscribed:

        await callback.answer("Вы не подписаны", show_alert=True)

    else:

        await callback.message.edit_text(
            "Выберите категорию программ:",
            reply_markup=categories_menu()
        )


# открыть категорию
@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def open_category(callback: types.CallbackQuery):

    category = callback.data.replace("cat_", "")

    await callback.message.edit_text(
        f"Категория: {category}",
        reply_markup=programs_menu(category)
    )


# отправка программы
@dp.callback_query(lambda c: c.data.startswith("prog_"))
async def send_program(callback: types.CallbackQuery):

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    data = callback.data.replace("prog_", "")
    category, file = data.split("|")

    path = f"{BASE_DIR}/{category}/{file}"

    # удаляем старую программу
    if user_id in user_program_message:

        try:
            await bot.delete_message(
                chat_id,
                user_program_message[user_id]
            )
        except:
            pass

    await callback.answer()

    doc = await callback.message.answer_document(
        types.FSInputFile(path)
    )

    user_program_message[user_id] = doc.message_id

    await callback.message.answer(
        "А если хочешь индивидуальную программу, со всеми корректировками лично под тебя "
        "то можешь ознакомиться со всеми ПРАЙСАМИ тут:\n@wedeni_skeleTT"
    )


# кнопка поддержки автора
@dp.callback_query(lambda c: c.data == "support")
async def support_author(callback: types.CallbackQuery):

    await callback.answer()

    await callback.message.answer_photo(
        types.FSInputFile("images/qr.png"),
        caption="Если хочешь поддержать автора в его продвижении, "
        "то наведи камеру телефона на QR-код"
    )


# назад
@dp.callback_query(lambda c: c.data == "back")
async def back(callback: types.CallbackQuery):

    await callback.message.edit_text(
        "Выберите категорию программ:",
        reply_markup=categories_menu()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())