from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from database import is_blocked, check_rate_limit, add_log
from config import MAX_REQUESTS_PER_MINUTE


class SecurityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None

        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user:
            # Проверка блокировки
            if is_blocked(user.id):
                if isinstance(event, Message):
                    await event.answer("⛔ Вы заблокированы.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⛔ Вы заблокированы.", show_alert=True)
                return

            # Проверка rate limit
            if not check_rate_limit(user.id, MAX_REQUESTS_PER_MINUTE):
                if isinstance(event, Message):
                    await event.answer("⚠️ Слишком много запросов. Подождите минуту.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⚠️ Слишком много запросов.", show_alert=True)
                add_log(user.id, "rate_limit", f"Превышен лимит запросов")
                return

        return await handler(event, data)
