from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Access denied.")
        return

    await message.answer(
        "🔧 *Admin Panel*\n\n"
        "Available commands:\n"
        "/stats — order statistics (coming soon)\n"
        "/broadcast — message all users (coming soon)\n\n"
        "Orders arrive here automatically when customers pay.",
        parse_mode="Markdown"
    )
