from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from products import CATEGORIES, get_by_category


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💨 Электронные сигареты", callback_data="menu:vapes")
    builder.button(text="🐂 Снюс D.L.T.A.", callback_data="category:snus")
    builder.button(text="🛒 Моя корзина", callback_data="cart:view")
    builder.button(text="💬 Задать вопрос", callback_data="support:ask")
    builder.adjust(1)
    return builder.as_markup()


def vapes_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💨 WAKA soPro 20000", callback_data="category:waka")
    builder.button(text="💨 PAFOS 20000", callback_data="category:pafos")
    builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def category_kb(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in get_by_category(category):
        builder.button(text=p["name"].split(" - ")[1] if " - " in p["name"] else p["name"], callback_data=f"product:{p['id']}")
    if category in ["waka", "pafos"]:
        builder.button(text="🔙 Назад", callback_data="menu:vapes")
    else:
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


def cart_kb(items: dict
