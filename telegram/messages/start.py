from telegram.bot import BaseTelegramCommandHandler
from telebot import types
from .menu import home_markup


class StartCommandHandler(BaseTelegramCommandHandler):
    command = "start"

    def handler(self, message: types.Message, command: str, args: list[str]):
        if args:
            return

        self.messenger.reply_to(
            message,
            "Welcome to unitap official telegram bot, how can i help you?",
            reply_markup=home_markup,
        )
