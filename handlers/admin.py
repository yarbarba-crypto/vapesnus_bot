from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS, ADMIN_PASSWORD
from database import get_stats, get_all_users, block_user, unblock_user, add_log

router = Router()

verified_admins = set()


class AdminState(StatesGroup):
    waiting_password = State()
    waiting_broadcast = State()
    waiting_block_id = State()
    waiting_unblock_id = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def is_verified(user_id: int) -> bool:
    return user_id in verified_admins


def admin_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="admin:stats")
    builder.button(text="📢 Рассылка", callback_data="admin:broadcast")
    builder.button(text="🚫 Заблокировать", callback_data="admin:block")
    builder.button(text="✅ Разблокировать", callback_data="admin:unblock")
    builder.adjust(2)
    return builder.as_markup()


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        add_log(message.from_user.id, "admin_attempt", "Попытка доступа к админке")
        await message.answer("⛔ Нет доступа.")
        return

    if is_verified(message.from_user.id):
        await message.answer(
            "🔧 *Панель администратора*",
            parse_mode="Markdown",
            reply_markup=admin_kb()
        )
        return

    await state.set_state(AdminState.waiting_password)
    await message.answer("🔐 Введите пароль администратора:")


@router.message(StateFilter(AdminState.waiting_password))
async def check_password(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    if message.text == ADMIN_PASSWORD:
        verified_admins.add(message.from_user.id)
        await state.clear()
        await message.delete()
        await message.answer(
            "✅ Доступ разрешён!\n\n🔧 *Панель администратора*",
            parse_mode="Markdown",
            reply_markup=admin_kb()
        )
    else:
        add_log(message.from_user.id, "wrong_password", "Неверный пароль админа")
        await message.delete()
        await message.answer("❌ Неверный пароль. Попробуйте ещё раз:")


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id) or not is_verified(callback.from_user.id):
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
    if not is_admin(callback.from_user.id) or not is_verified(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(AdminState.waiting_broadcast)
    await callback.message.answer("📢 Напиши сообщение для рассылки:")
    await callback.answer()


@router.message(StateFilter(AdminState.waiting_broadcast))
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


@router.callback_query(F.data == "admin:block")
async def start_block(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id) or not is_verified(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(AdminState.waiting_block_id)
    await callback.message.answer("🚫 Введи ID пользователя для блокировки:")
    await callback.answer()


@router.message(StateFilter(AdminState.waiting_block_id))
async def do_block(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        block_user(user_id, "Заблокирован админом")
        await state.clear()
        await message.answer(f"✅ Пользователь `{user_id}` заблокирован.", parse_mode="Markdown")
    except ValueError:
        await message.answer("❌ Введи числовой ID пользователя.")


@router.callback_query(F.data == "admin:unblock")
async def start_unblock(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id) or not is_verified(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(AdminState.waiting_unblock_id)
    await callback.message.answer("✅ Введи ID пользователя для разблокировки:")
    await callback.answer()


@router.message(StateFilter(AdminState.waiting_unblock_id))
async def do_unblock(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        unblock_user(user_id)
        await state.clear()
        await message.answer(f"✅ Пользователь `{user_id}` разблокирован.", parse_mode="Markdown")
    except ValueError:
        await message.answer("❌ Введи числовой ID пользователя.")
