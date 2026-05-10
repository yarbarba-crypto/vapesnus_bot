from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import cart_kb, confirm_order_kb
from products import get_product

router = Router()


def get_cart(data: dict) -> dict:
    return data.get("cart", {})


def format_cart(cart: dict) -> str:
    if not cart:
        return "🛒 Ваша корзина пуста."
    lines = ["🛒 *Ваша корзина:*\n"]
    total = 0
    for product_id, qty in cart.items():
        p = get_product(product_id)
        if p:
            subtotal = p["price"] * qty
            total += subtotal
            lines.append(f"• {p['name']} × {qty} = {subtotal} ⭐")
    lines.append(f"\n💰 *Итого: {total} звёзд*")
    return "\n".join(lines)


@router.callback_query(F.data.startswith("cart:add:"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[2]
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    data = await state.get_data()
    cart = get_cart(data)
    cart[product_id] = cart.get(product_id, 0) + 1
    await state.update_data(cart=cart)

    await callback.answer(f"✅ {product['name']} добавлен в корзину!")


@router.callback_query(F.data == "cart:view")
async def view_cart(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = get_cart(data)
    text = format_cart(cart)
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=cart_kb(cart)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cart:remove:"))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[2]
    data = await state.get_data()
    cart = get_cart(data)

    if product_id in cart:
        del cart[product_id]
        await state.update_data(cart=cart)

    text = format_cart(cart)
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=cart_kb(cart)
    )
    await callback.answer("Товар удалён.")


@router.callback_query(F.data == "cart:checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = get_cart(data)

    if not cart:
        await callback.answer("Ваша корзина пуста!", show_alert=True)
        return

    total = sum(get_product(pid)["price"] * qty for pid, qty in cart.items() if get_product(pid))
    text = format_cart(cart) + f"\n\nГотовы оплатить *{total} звёзд*?"
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=confirm_order_kb()
    )
    await callback.answer()
