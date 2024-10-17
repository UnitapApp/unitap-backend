from telegram.bot import BaseTelegramCommandHandler
from telebot import types


class StartCommandHandler(BaseTelegramCommandHandler):
    command = "start"

    def handler(self, message: types.Message, command: str, args: list[str]):
        if args:
            return

        markup = types.ReplyKeyboardMarkup()

        markup.add(types.KeyboardButton("Connect your account"))

        markup.add(types.KeyboardButton("Stats of gastap"))

        markup.add(types.KeyboardButton("Report bug 🪲"))

        markup.add(types.KeyboardButton("About Unitap ❓"))

        self.messenger.reply_to(
            message,
            "Welcome to unitap official telegram bot, how can i help you?",
            reply_markup=markup,
        )
