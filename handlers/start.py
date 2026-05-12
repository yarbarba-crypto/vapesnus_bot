from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я согласен, мне есть 18 лет", callback_data="disclaimer:accept")
    builder.adjust(1)
    await message.answer(
        "⚠️ *Дисклеймер*\n\n"
        "Данный бот носит исключительно *ознакомительный характер* "
        "и не является публичной офертой.\n\n"
        "🚬 Никотин вызывает сильную зависимость и наносит вред здоровью. "
        "Употребление никотиносодержащей продукции противопоказано лицам "
        "до 18 лет, беременным и кормящим женщинам.\n\n"
        "Нажимая кнопку ниже, вы подтверждаете что вам *исполнилось 18 лет* "
        "и вы ознакомились с данным предупреждением.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "disclaimer:accept")
async def accept_disclaimer(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "👋 Добро пожаловать в Dark Store!\n\n"
        "📖 Здесь вы можете ознакомиться с нашим ассортиментом "
        "и оставить заявку на интересующий товар.\n\n"
        "Выбери категорию:",
        reply_markup=main_menu_kb()
    )
    await callback.answer()
