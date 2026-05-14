from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_user_orders

router = Router()

STATUS_MAP = {
    "new": "🆕 Новая",
    "accepted": "✅ Принята в работу",
    "done": "📦 Выполнена",
}


@router.callback_query(F.data == "my:orders")
async def show_my_orders(callback: CallbackQuery):
    orders = get_user_orders(callback.from_user.id)

    if not orders:
        await callback.message.answer(
            "📋 У вас пока нет заявок.\n\n"
            "Выберите товар и нажмите '📝 Оставить заявку'!"
        )
        await callback.answer()
        return

    text = "📋 *Ваши последние заявки:*\n\n"
    for order in orders:
        status = STATUS_MAP.get(order["status"], order["status"])
        date = order["created_at"][:10]
        text += (
            f"*Заявка #{order['id']}*\n"
            f"📦 {order['product_name']}\n"
            f"📅 {date}\n"
            f"Статус: {status}\n\n"
        )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()
