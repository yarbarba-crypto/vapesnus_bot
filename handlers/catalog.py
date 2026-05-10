from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import main_menu_kb, vapes_menu_kb, category_kb, product_kb
from products import get_product, CATEGORIES

router = Router()


@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Выбери категорию:",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "menu:vapes")
async def show_vapes_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "💨 Выбери марку электронной сигареты:",
        reply_markup=vapes_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def show_category(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    labels = {
        "waka": "💨 WAKA soPro 20000",
        "pafos": "💨 PAFOS 20000",
        "snus": "🐂 D.L.T.A. Red Bull Edition",
    }
    label = labels.get(category, category)
    await callback.message.delete()
    await callback.message.answer(
        f"{label}\n\nВыбери вкус:",
        reply_markup=category_kb(category)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery):
    product_id = callback.data.split(":")[1]
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    caption = (
        f"*{product['name']}*\n\n"
        f"{product['description']}\n\n"
        f"💫 Цена: *{product['price']} Stars*"
    )
