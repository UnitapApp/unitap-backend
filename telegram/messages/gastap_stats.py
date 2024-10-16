from telegram.bot import BaseTelegramMessageHandler
from telebot import types


class StartCommandHandler(BaseTelegramMessageHandler):
    message = "Stats of gastap"

    def handler(self, message: types.Message):
        pass
