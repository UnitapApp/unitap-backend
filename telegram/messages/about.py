from telegram.bot import BaseTelegramMessageHandler
from telebot import types


about_text = """**About Unitap**

Welcome to Unitap, your smart companion for managing tasks, getting updates, and automating processes! Whether you're working on a project, organizing events, or just need help staying on top of things, Unitap is here to assist.

With Unitap, you can:
\- **Receive timely notifications** for important events.
\- **Submit and track issues** directly within your workspace.
\- **Connect with services** and streamline your workflow.
\- **Ask for help or request hints** to navigate challenges.

Unitap is designed to integrate seamlessly with your tools, making your work life smoother and more efficient. Start interacting today by typing `/help` to see available commands!

read more here https://unitap.app/about
"""


class AboutMessageHandler(BaseTelegramMessageHandler):
    message = "About Unitap ❓"

    def handler(self, message: types.Message):
        self.messenger.reply_to(message, text=about_text, parse_mode="MarkdownV2")
