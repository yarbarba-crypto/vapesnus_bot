from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from config import ADMIN_IDS

router = Router()


class SupportState(StatesGroup):
    waiting_for_question = State()
    waiting_for_reply = State()


def admin_reply_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ответить", callback_data=f"reply:{user_id}")
    return builder.as_markup()


# Покупатель пишет /ask
@router.message(Command("ask"))
async def ask_question(message: Message, state: FSMContext):
    await state.set_state(SupportState.waiting_for_question)
    await message.answer("📝 Напишите ваш вопрос следующим сообщением:")


# Покупатель пишет вопрос
@router.message(SupportState.waiting_for_question)
async def receive_question(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"📨 *Новое сообщение от покупателя*\n\n"
                f"👤 [{user.full_name}](tg://user?id={user.id})\n"
                f"🆔 ID: `{user.id}`\n\n"
                f"💬 {message.text}",
                parse_mode="Markdown",
                reply_markup=admin_reply_kb(user.id)
            )
        except Exception:
            pass
    await message.answer("✅ Ваш вопрос отправлен! Ожидайте ответа.")
    await state.clear()


# Админ нажимает "Ответить"
@router.callback_query(F.data.startswith("reply:"))
async def admin_reply_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callbac
