from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import admin_reply_kb, main_menu_kb
from products import get_product
from config import ADMIN_IDS
from database import add_order, update_order_status, add_user

router = Router()


def order_admin_kb(order_id: int, user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принято в работу", callback_data=f"accept:{order_id}:{user_id}")
    builder.button(text="💬 Ответить", callback_data=f"reply:{user_id}")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith("order:"))
async def leave_order(callback: CallbackQuery, bot: Bot):
    product_id = callback.data.split(":")[1]
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    user = callback.from_user
    add_user(user.id, user.username or "", user.full_name)
    order_id = add_order(user.id, product["name"], "Москва")

    await callback.message.answer(
        f"✅ Ваша заявка *#{order_id}* отправлена!\n\n"
        f"🛍 Товар: *{product['name']}*\n\n"
        f"Мы свяжемся с вами в ближайшее время.",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🛍 *Новая заявка #{order_id}!*\n\n"
                f"👤 [{user.full_name}](tg://user?id={user.id})\n"
                f"🆔 ID: `{user.id}`\n\n"
                f"📦 Товар: *{product['name']}*",
                parse_mode="Markdown",
                reply_markup=order_admin_kb(order_id, user.id)
            )
        except Exception:
            pass

    await callback.answer()


@router.callback_query(F.data.startswith("accept:"))
async def accept_order(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":")
    order_id = int(parts[1])
    user_id = int(parts[2])

    update_order_status(order_id, "accepted")

    try:
        await bot.send_message(
            user_id,
            f"✅ *Ваша заявка #{order_id} принята в работу!*\n\n"
            f"Мы свяжемся с вами в ближайшее время для уточнения деталей.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Заявка #{order_id} принята в работу!")
    await callback.answer()
