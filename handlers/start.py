from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Welcome to our store!\n\n"
        "We sell premium disposable vapes and nicotine pouches.\n"
        "Browse our catalogue and order with Telegram Stars ⭐\n\n"
        "Choose a category to get started:",
        reply_markup=main_menu_kb()
    )
