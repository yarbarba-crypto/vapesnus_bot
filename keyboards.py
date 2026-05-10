from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from products import CATEGORIES, get_by_category


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        builder.button(text=label, callback_data=f"category:{key}")
    builder.button(text="🛒 My Cart", callback_data="cart:view")
    builder.adjust(1)
    return builder.as_markup()


def category_kb(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in get_by_category(category):
        builder.button(text=p["name"], callback_data=f"product:{p['id']}")
    builder.button(text="🔙 Back", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def product_kb(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Add to Cart", callback_data=f"cart:add:{product_id}")
    builder.button(text="🛒 View Cart",   callback_data="cart:view")
    builder.button(text="🔙 Back",        callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(items: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product_id in items:
        builder.button(
            text=f"❌ Remove item",
            callback_data=f"cart:remove:{product_id}"
        )
    if items:
        builder.button(text="✅ Checkout", callback_data="cart:checkout")
    builder.button(text="🔙 Back to Shop", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def confirm_order_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💫 Pay with Stars", callback_data="order:pay")
    builder.button(text="❌ Cancel",          callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
