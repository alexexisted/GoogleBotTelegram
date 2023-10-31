from aiogram.filters import Command
from aiogram import types, Router, Bot

router = Router()

@router.message(Command("start"))
async def say_hello(message: types.Message):
    kb = [
        [types.KeyboardButton(text = "Add an event")],
        [types.KeyboardButton(text = "Delete an event")],
        [types.KeyboardButton(text = "look when we have a free time")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard = kb,
        resize_keyboard = True,
        input_field_placeholder = "Choose the option"
    )
    await message.answer("what do you want to do with your calendar?", reply_markup = keyboard)
