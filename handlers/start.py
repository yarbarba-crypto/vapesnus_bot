from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Dark Store!\n\n"
        "📖 Здесь вы можете ознакомиться с нашим ассортиментом "
        "и оставить заявку на интересующий товар.\n\n"
        "Мы свяжемся с вами в ближайшее время!\n\n"
        "Выбери категорию:",
        reply_markup=main_menu_kb()
    )
