from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from products import get_by_category


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💨 Электронные сигареты", callback_data="menu:vapes")
    builder.button(text="🟢 Снюс", callback_data="menu:snus")
    builder.button(text="💬 Задать вопрос", callback_data="support:ask")
    builder.adjust(1)
    return builder.as_markup()


def vapes_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💨 WAKA soPro 20000", callback_data="category:waka")
    builder.button(text="💨 PAFOS 20000", callback_data="category:pafos")
    builder.button(text="💨 PUFFMI Mosh 40000", callback_data="category:puffmi")
    builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def snus_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🐂 D.L.T.A. Red Bull Edition", callback_data="category:snus")
    builder.button(text="🇸🇪 Oden's (Швеция)", callback_data="category:odens")
    builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def category_kb(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in get_by_category(category):
        name = p["name"].split(" - ")[1] if " - " in p["name"] else p["name"]
        builder.button(text=name, callback_data=f"product:{p['id']}")
    if category in ["waka", "pafos", "puffmi"]:
        builder.button(text="🔙 Назад", callback_data="menu:vapes")
    elif category in ["snus", "odens"]:
        builder.button(text="🔙 Назад", callback_data="menu:snus")
    else:
        builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def product_kb(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Оставить заявку", callback_data=f"order:{product_id}")
    builder.button(text="🔙 Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_reply_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Ответить", callback_data=f"reply:{user_id}")
    builder.adjust(1)
    return builder.as_markup()
