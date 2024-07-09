from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from repository.user import UsersRepository


class AuthMiddleware(BaseMiddleware):

    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        self.users_repo.create_user(event.from_user.id)
        return await handler(event, data)
