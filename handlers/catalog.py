from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import main_menu_kb, vapes_menu_kb, snus_menu_kb, category_kb, product_kb
from products import get_product

router = Router()


@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "📖 Добро пожаловать в каталог!\n\nВыбери категорию:",
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


@router.callback_query(F.data == "menu:snus")
async def show_snus_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "🟢 Выбери марку снюса:",
        reply_markup=snus_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def show_category(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    labels = {
        "waka": "💨 WAKA soPro 20000",
        "pafos": "💨 PAFOS 20000",
        "puffmi": "💨 PUFFMI Mosh 40000",
        "snus": "🐂 D.L.T.A. Red Bull Edition",
        "odens": "🇸🇪 Oden's (Швеция)",
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
        f"{product['description']}"
    )

    try:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=product["photo"],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=product_kb(product_id)
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            caption,
            parse_mode="Markdown",
            reply_markup=product_kb(product_id)
        )
    await callback.answer()
