from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from products import CATEGORIES, get_by_category


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        builder.button(text=label, callback_data=f"category:{key}")
    builder.button(text="🛒 Моя корзина", callback_data="cart:view")
    builder.adjust(1)
    return builder.as_markup()


def category_kb(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in get_by_category(category):
        builder.button(text=p["name"], callback_data=f"product:{p['id']}")
    builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def product_kb(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить в корзину", callback_data=f"cart:add:{product_id}")
    builder.button(text="🛒 Перейти в корзину", callback_data="cart:view")
    builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(items: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product_id in items:
        builder.button(
            text="❌ Удалить товар",
            callback_data=f"cart:remove:{product_id}"
        )
    if items:
        builder.button(text="✅ Оформить заказ", callback_data="cart:checkout")
    builder.button(text="🔙 Вернуться в магазин", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def confirm_order_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💫 Оплатить звёздами", callback_data="order:pay")
    builder.button(text="❌ Отмена", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
