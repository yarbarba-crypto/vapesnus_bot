from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS
from database import get_stats, get_all_users

router = Router()


class BroadcastState(StatesGroup):
    waiting = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="admin:stats")
    builder.button(text="📢 Рассылка", callback_data="admin:broadcast")
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer(
        "🔧 *Панель администратора*",
        parse_mode="Markdown",
        reply_markup=admin_kb()
    )


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    stats = get_stats()
    text = (
        f"📊 *Статистика*\n\n"
        f"👥 Всего пользователей: *{stats['total_users']}*\n"
        f"📦 Всего заявок: *{stats['total_orders']}*\n"
        f"🆕 Новых заявок: *{stats['new_orders']}*\n"
        f"✅ Принято в работу: *{stats['accepted_orders']}*"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting)
    await callback.message.answer(
        "📢 Напиши сообщение для рассылки всем пользователям:"
    )
    await callback.answer()


@router.message(StateFilter(BroadcastState.waiting))
async def send_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    users = get_all_users()
    sent = 0
    failed = 0

    for user_id in users:
        try:
            await bot.send_message(
                user_id,
                f"📢 *Сообщение от Dark Store:*\n\n{message.text}",
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        f"✅ Рассылка завершена!\n\n"
        f"📨 Отправлено: *{sent}*\n"
        f"❌ Не доставлено: *{failed}*",
        parse_mode="Markdown"
    )
