from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from keyboards import admin_reply_kb, main_menu_kb
from products import get_product
from config import ADMIN_IDS

router = Router()


class AdminReply(StatesGroup):
    waiting = State()


@router.callback_query(F.data.startswith("order:"))
async def leave_order(callback: CallbackQuery, bot: Bot):
    product_id = callback.data.split(":")[1]
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    user = callback.from_user
    text = (
        f"📝 *Новая заявка!*\n\n"
        f"👤 [{user.full_name}](tg://user?id={user.id})\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"🛍 Товар: *{product['name']}*"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                text,
                parse_mode="Markdown",
                reply_markup=admin_reply_kb(user.id)
            )
        except Exception:
            pass

    await callback.message.answer(
        "✅ Ваша заявка отправлена!\n\n"
        "Мы свяжемся с вами в ближайшее время.",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reply:"))
async def cb_reply(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = int(callback.data.split(":")[1])
    await state.update_data(reply_to=user_id)
    await state.set_state(AdminReply.waiting)
    await callback.message.answer("✏️ Напишите ответ покупателю:")
    await callback.answer()


@router.message(StateFilter(AdminReply.waiting))
async def send_reply(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("reply_to")
    await state.clear()
    if user_id:
        await bot.send_message(
            user_id,
            f"💬 *Ответ от магазина:*\n\n{message.text}",
            parse_mode="Markdown"
        )
        await message.answer("✅ Ответ отправлен!")
