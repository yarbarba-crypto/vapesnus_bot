from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS

router = Router()


class SupportState(StatesGroup):
    waiting_for_reply = State()


def admin_reply_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ответить", callback_data=f"reply:{user_id}")
    return builder.as_markup()


# Покупатель пишет /support или "поддержка"
@router.message(F.text.lower().in_(["поддержка", "/support", "помощь", "/help"]))
async def support_request(message: Message):
    await message.answer(
        "📝 Напишите ваш вопрос, и мы ответим вам в ближайшее время!"
    )


# Покупатель пишет вопрос — пересылаем админу
@router.message(F.text & ~F.text.startswith("/"))
async def forward_to_admin(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    # Не пересылаем если это не вопрос (просто навигация)
    if data.get("in_support"):
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
        await state.update_data(in_support=False)


# Команда для покупателя начать диалог с поддержкой
@router.message(F.text.startswith("/ask"))
async def ask_question(message: Message, state: FSMContext):
    await state.update_data(in_support=True)
    await message.answer(
        "📝 Напишите ваш вопрос следующим сообщением:"
    )


# Админ нажимает "Ответить"
@router.callback_query(F.data.startswith("reply:"))
async def admin_reply_start(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    await state.update_data(reply_to=user_id)
    await state.set_state(SupportState.waiting_for_reply)
    await callback.message.answer(
        f"✏️ Напишите ответ покупателю (ID: {user_id}):"
    )
    await callback.answer()


# Админ пишет ответ — отправляем покупателю
@router.message(SupportState.waiting_for_reply)
async def send_reply(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("reply_to")

    if user_id:
        try:
            await bot.send_message(
                user_id,
                f"💬 *Ответ от поддержки:*\n\n{message.text}",
                parse_mode="Markdown"
            )
            await message.answer("✅ Ответ отправлен покупателю!")
        except Exception:
            await message.answer("❌ Не удалось отправить сообщение.")

    await state.clear()
