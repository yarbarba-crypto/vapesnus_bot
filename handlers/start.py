from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в наш магазин!\n\n"
        "Мы продаём одноразовые вейпы и никотиновые пауч​и.\n"
        "Выбирай товары и оплачивай звёздами Telegram ⭐\n\n"
        "Выбери категорию:",
        reply_markup=main_menu_kb()
    )
