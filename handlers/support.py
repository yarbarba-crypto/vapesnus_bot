from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from config import ADMIN_IDS

router = Router()


class AdminReply(StatesGroup):
    waiting = State()


def reply_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ответить", callback_data=f"reply:{user_id}")
    return builder.as_markup()


# Шаг 1: покупатель пишет /ask
@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📝 Напишите ваш вопрос:")
    await state.set_state("waiting_question")


# Шаг 2: покупатель пишет вопрос
@router.message(F.text, F.state == "waiting_question")
async def got_question(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    await state.clear()
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"📨 *Вопрос от покупателя*\n\n"
            f"👤 {user.full_name}\n"
            f"🆔 `{user.id}`\n\n"
            f"💬 {message.text}",
            parse_mode="Markdown",
            reply_markup=reply_kb(user.id)
        )
    await message.answer("✅ Вопрос отправлен! Ожидайте ответа.")


# Шаг 3: админ нажимает "Ответить"
@router.callback_query(F.data.startswith("reply:"))
async def cb_reply(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = int(callback.data.split(":")[1])
    await state.update_data(reply_to=user_id)
    await state.set_state(AdminReply.waiting)
    await callback.message.answer(f"✏️ Напишите ответ покупателю:")
    await callback.answer()


# Шаг 4: админ пишет ответ
@router.message(AdminReply.waiting)
async def send_reply(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("reply_to")
    await state.clear()
    if user_id:
        await bot.send_message(
            user_id,
            f"💬 *Ответ от поддержки:*\n\n{message.text}",
            parse_mode="Markdown"
        )
        await message.answer("✅ Ответ отправлен!")
