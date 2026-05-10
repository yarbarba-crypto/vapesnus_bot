from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.fsm.context import FSMContext
from products import get_product
from config import ADMIN_IDS

router = Router()


def get_cart(data: dict) -> dict:
    return data.get("cart", {})


@router.callback_query(F.data == "order:pay")
async def send_invoice(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    cart = get_cart(data)
    if not cart:
        await callback.answer("Cart is empty!", show_alert=True)
        return

    prices = []
    description_lines = []
    for product_id, qty in cart.items():
        p = get_product(product_id)
        if p:
            prices.append(LabeledPrice(label=f"{p['name']} × {qty}", amount=p["price"] * qty))
            description_lines.append(f"{p['name']} × {qty}")

    description = "\n".join(description_lines)

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Your Order",
        description=description,
        payload="order_payload",
        currency="XTR",
        prices=prices,
        provider_token="",
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    cart = get_cart(data)
    payment = message.successful_payment

    lines = []
    for product_id, qty in cart.items():
        p = get_product(product_id)
        if p:
            lines.append(f"• {p['name']} × {qty}")

    order_text = "\n".join(lines)
    stars_paid = payment.total_amount

    await message.answer(
        f"✅ *Payment received! Thank you!*\n\n"
        f"💫 Paid: {stars_paid} Stars\n\n"
        f"*Your order:*\n{order_text}\n\n"
        f"We'll process your order shortly and reach out with delivery details.",
        parse_mode="Markdown"
    )

    user = message.from_user
    admin_text = (
        f"🛍 *New Order!*\n\n"
        f"👤 Customer: [{user.full_name}](tg://user?id={user.id})\n"
        f"🆔 User ID: `{user.id}`\n"
        f"💫 Paid: {stars_paid} Stars\n\n"
        f"*Items:*\n{order_text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, parse_mode="Markdown")
        except Exception:
            pass

    await state.update_data(cart={})
