from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import main_menu_kb
from products import get_product
from config import ADMIN_IDS
from database import add_order, update_order_status, add_user

router = Router()


class OrderState(StatesGroup):
    waiting_delivery = State()
    waiting_postamat = State()
    waiting_kladka = State()
    waiting_photo = State()


def delivery_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Постамат", callback_data="delivery:postamat")
    builder.button(text="🗺 Закладка", callback_data="delivery:kladka")
    builder.adjust(1)
    return builder.as_markup()


def photo_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Отправить фото", callback_data="photo:yes")
    builder.button(text="➡️ Пропустить", callback_data="photo:skip")
    builder.adjust(1)
    return builder.as_markup()


def order_admin_kb(order_id: int, user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принято в работу", callback_data=f"accept:{order_id}:{user_id}")
    builder.button(text="💬 Ответить", callback_data=f"reply:{user_id}")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith("order:"))
async def leave_order(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[1]
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    user = callback.from_user
    add_user(user.id, user.username or "", user.full_name)
    await state.update_data(product_id=product_id)
    await state.set_state(OrderState.waiting_delivery)

    await callback.message.answer(
        f"🛍 *{product['name']}*\n\nВыбери способ доставки:",
        parse_mode="Markdown",
        reply_markup=delivery_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "delivery:postamat", StateFilter(OrderState.waiting_delivery))
async def choose_postamat(callback: CallbackQuery, state: FSMContext):
    await state.update_data(delivery_type="postamat")
    await state.set_state(OrderState.waiting_postamat)
    await callback.message.answer(
        "📦 *Постамат*\n\nНапиши адрес или название ближайшего постамата:",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "delivery:kladka", StateFilter(OrderState.waiting_delivery))
async def choose_kladka(callback: CallbackQuery, state: FSMContext):
    await state.update_data(delivery_type="kladka")
    await state.set_state(OrderState.waiting_kladka)
    await callback.message.answer(
        "🗺 *Закладка*\n\nНапиши район или станцию метро:",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(StateFilter(OrderState.waiting_postamat))
async def got_postamat(message: Message, state: FSMContext):
    await state.update_data(delivery_info=f"📦 Постамат: {message.text}")
    await state.set_state(OrderState.waiting_photo)
    await message.answer(
        "📸 Хочешь прикрепить фото товара который ищешь?",
        reply_markup=photo_kb()
    )


@router.message(StateFilter(OrderState.waiting_kladka))
async def got_kladka(message: Message, state: FSMContext):
    await state.update_data(delivery_info=f"🗺 Закладка: {message.text}")
    await state.set_state(OrderState.waiting_photo)
    await message.answer(
        "📸 Хочешь прикрепить фото товара который ищешь?",
        reply_markup=photo_kb()
    )


@router.callback_query(F.data == "photo:yes", StateFilter(OrderState.waiting_photo))
async def ask_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_photo)
    await callback.message.answer("📸 Отправь фото товара:")
    await callback.answer()


@router.callback_query(F.data == "photo:skip", StateFilter(OrderState.waiting_photo))
async def skip_photo(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await send_order(callback.message, state, bot, callback.from_user, photo_id=None)
    await callback.answer()


@router.message(StateFilter(OrderState.waiting_photo), F.photo)
async def got_photo(message: Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    await send_order(message, state, bot, message.from_user, photo_id=photo_id)


async def send_order(message: Message, state: FSMContext, bot: Bot, user, photo_id=None):
    data = await state.get_data()
    product = get_product(data["product_id"])
    delivery_info = data.get("delivery_info", "Не указано")

    order_id = add_order(user.id, product["name"], delivery_info)
    await state.clear()

    await message.answer(
        f"✅ Заявка *#{order_id}* отправлена!\n\n"
        f"🛍 Товар: *{product['name']}*\n"
        f"{delivery_info}\n\n"
        f"Мы свяжемся с вами в ближайшее время.",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

    admin_text = (
        f"🛍 *Новая заявка #{order_id}!*\n\n"
        f"👤 [{user.full_name}](tg://user?id={user.id})\n"
        f"🆔 ID: `{user.id}`\n"
        f"📎 Тег: @{user.username if user.username else 'нет тега'}\n\n"
        f"📦 Товар: *{product['name']}*\n"
        f"{delivery_info}"
    )

    for admin_id in ADMIN_IDS:
        try:
            if photo_id:
                await bot.send_photo(
                    admin_id,
                    photo=photo_id,
                    caption=admin_text,
                    parse_mode="Markdown",
                    reply_markup=order_admin_kb(order_id, user.id)
                )
            else:
                await bot.send_message(
                    admin_id,
                    admin_text,
                    parse_mode="Markdown",
                    reply_markup=order_admin_kb(order_id, user.id)
                )
        except Exception:
            pass


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
            f"Мы свяжемся с вами в ближайшее время.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Заявка #{order_id} принята в работу!")
    await callback.answer()
