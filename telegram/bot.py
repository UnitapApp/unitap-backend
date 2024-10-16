from authentication.models import UserProfile
from django.conf import settings
from abc import ABC, abstractmethod
from telebot import types

import telebot
import time
import logging


logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.TELEGRAM_BOT_API_KEY)

MAX_REQUESTS_PER_SECOND = 30


class TelegramRateLimiter:
    """
    A rate limiter class for controlling the frequency of Telegram API requests.

    This class ensures that the number of API requests sent per second does not exceed
    the defined maximum rate by enforcing a delay between requests when needed.

    Attributes:
        first_request_time (float): The time the first request in the current batch was sent.
        requests_sent (int): The number of requests sent in the current batch.
    """

    def __init__(self, max_requests_per_second=MAX_REQUESTS_PER_SECOND):
        """
        Initialize the rate limiter with the maximum number of requests per second.

        Args:
            max_requests_per_second (int): The maximum number of requests allowed per second.
        """
        self.first_request_time = 0.0
        self.requests_sent = 0
        self.max_requests_per_second = max_requests_per_second

    def send_telegram_request(self, func, *args, **kwargs):
        """
        Send a Telegram API request, enforcing rate limits.

        This method calculates the elapsed time since the first request, and if the number of
        requests exceeds the allowed rate, it introduces a delay to avoid hitting the limit.

        Args:
            func (callable): The function that sends the actual Telegram API request.
            *args: Positional arguments to pass to the `func`.
            **kwargs: Keyword arguments to pass to the `func`.

        Returns:
            The result of the API request or `None` if an exception occurs.
        """
        current_time = time.time()
        elapsed_time = current_time - self.first_request_time

        # Check if we've sent too many requests within the current second
        if self.requests_sent >= self.max_requests_per_second:
            # Calculate the delay needed to respect the rate limit
            delay_time = max(1 - elapsed_time, 0)
            time.sleep(delay_time)
            # Reset the request counter and time after waiting
            self.requests_sent = 0
            self.first_request_time = time.time()

        try:
            # Attempt to execute the provided function (API request)
            result = func(*args, **kwargs)
        except Exception as e:
            # Handle any exceptions that occur during the API request
            logger.error(f"[T] Exception occurred while making the request: {e}")
            result = None

        # Reset the timer for the first request in the next batch if necessary
        if self.requests_sent == 0:
            self.first_request_time = time.time()

        # Increment the count of requests sent
        self.requests_sent += 1

        return result


class TelegramMessenger:
    """
    A singleton class responsible for managing Telegram bot interactions, including message,
    command, and callback handling. It uses rate limiting to ensure requests stay within Telegram's
    API limits.
    """

    # Rate limiter to prevent exceeding Telegram API limits
    limiter = TelegramRateLimiter()

    # Singleton instance of TelegramMessenger
    instance = None

    # Handlers for different types of bot interactions
    command_handlers: dict[str, "BaseTelegramCommandHandler"] = {}
    message_handlers: dict[str, "BaseTelegramMessageHandler"] = {}
    callback_handlers: dict[str, "BaseTelegramCallbackHandler"] = {}

    # List of admin users (can be extended to validate admin access)
    admin_users = []

    def __init__(self) -> None:
        """Private constructor for singleton behavior."""
        pass

    @staticmethod
    def get_instance():
        """
        Get the singleton instance of TelegramMessenger. If it doesn't exist, create it.

        Returns:
            TelegramMessenger: The singleton instance.
        """
        if TelegramMessenger.instance is None:
            TelegramMessenger.instance = TelegramMessenger()

        return TelegramMessenger.instance

    def handle_user_message(self, message: types.Message):
        """
        Handle a regular user message by dispatching it to the appropriate handler.

        Args:
            message (types.Message): The incoming message from the user.

        Returns:
            The result of the handler or None if no handler exists for the message.
        """
        instance = self.message_handlers.get(message.text)

        if not instance:
            return None

        return instance.handler(message)

    def handle_user_command(self, message: types.Message):
        """
        Handle a user command message (starting with '/') by dispatching it to the appropriate handler.

        Args:
            message (types.Message): The incoming command message.

        Returns:
            The result of the handler or None if no handler exists for the command.
        """
        args = message.text[1:].split()  # Split command and arguments
        command = args[0]

        instance = self.command_handlers.get(command)

        if not instance:
            return None

        return instance.handler(message, command, args[1:])

    def handle_callback_query(self, call: types.CallbackQuery):
        """
        Handle a callback query (typically from inline buttons) by dispatching it to the appropriate handler.

        Args:
            call (types.CallbackQuery): The incoming callback query.

        Returns:
            The result of the handler or None if no handler exists for the callback data.
        """
        cmd_parts = call.data.split(",")  # Assume callback data is comma-separated

        instance = self.callback_handlers.get(cmd_parts[0])

        if not instance:
            return None

        return instance.handler(call)

    def on_telegram_message(self, message: types.Message):
        """
        Handle an incoming Telegram message by determining if it's a command or a regular message.

        Args:
            message (types.Message): The incoming message.

        Returns:
            The result of either a command handler or message handler.
        """
        if message.text.startswith("/"):
            return self.handle_user_command(message)

        return self.handle_user_message(message)

    def ensure_webhook(self):
        """
        Ensure that the webhook is correctly set up for receiving Telegram updates.
        Uses the Telegram Bot API to register the webhook URL.
        """
        import requests

        # Replace with your webhook and Telegram Bot token
        webhook_url = "https://api.unitap.app/api/telegram/wh/"
        telegram_api_url = f"https://api.telegram.org/bot{bot.token}/setWebhook"

        # Register webhook with secret token for added security
        requests.post(
            telegram_api_url,
            data={"url": webhook_url, "secret_token": settings.TELEGRAM_BOT_API_SECRET},
        )

    def ready(self):
        """
        Prepare the bot by registering the message and callback handlers for processing updates.
        This is the setup function that connects Telegram message updates with handler functions.
        """
        bot.message_handler(func=lambda _: True)(
            lambda message: self.on_telegram_message(message)
        )

        bot.callback_query_handler(func=lambda _: True)(
            lambda call: self.handle_callback_query(call)
        )

    def send_message(self, user: UserProfile, *args, **kwargs) -> types.Message:
        """
        Send a message to a user using Telegram bot API with rate limiting.

        Args:
            user (UserProfile): The user profile to whom the message will be sent.
            *args: Positional arguments to pass to the bot.send_message function.
            **kwargs: Keyword arguments to pass to the bot.send_message function.

        Returns:
            types.Message: The sent message object.

        Raises:
            ValueError: If the user's Telegram connection is not available.
        """
        if not user.telegramconnections:
            raise ValueError("[T] User telegram connection must be present")

        return self.limiter.send_telegram_request(
            bot.send_message, chat_id=user.telegramconnections.user_id, *args, **kwargs
        )

    def update_query_messages(self, call: types.CallbackQuery, text: str, markup):
        """
        Update the text and markup of an existing inline query message (typically from inline buttons).

        Args:
            call (types.CallbackQuery): The callback query that triggered this action.
            text (str): The updated text for the message.
            markup: The updated inline keyboard markup for the message.

        Returns:
            The result of the bot.edit_message_text method.
        """
        return self.limiter.send_telegram_request(
            bot.edit_message_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
        )

    def reply_to(self, *args, **kwargs):
        """
        Send a reply to a message using the Telegram bot API with rate limiting.

        Args:
            *args: Positional arguments to pass to the bot.reply_to function.
            **kwargs: Keyword arguments to pass to the bot.reply_to function.

        Returns:
            The result of the bot.reply_to method.
        """
        return self.limiter.send_telegram_request(bot.reply_to, *args, **kwargs)


class TelegramEventHandler:

    messenger = TelegramMessenger.get_instance()

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot

    def handler(self, message: types.Message):
        raise NotImplementedError("[T] Subclasses should implement the handler method")


class BaseTelegramCommandHandler(TelegramEventHandler):
    """
    Base class for Telegram message handlers.
    Subclasses should define the command and implement the handler.
    """

    command = None
    required_role = None

    def handler(self, message: types.Message, command: str, args: list[str]):
        raise NotImplementedError("[T] Subclasses should implement the handler method")


class BaseTelegramMessageHandler(TelegramEventHandler):
    message = None
    required_role = None


class BaseTelegramCallbackHandler(TelegramEventHandler):
    callback = None
    required_role = None
    params = []

    def handler(self, callback: types.CallbackQuery):
        raise NotImplementedError("[T] Subclasses should implement the handler method")


def register_message_handlers():
    handlers = {}
    for subclass in BaseTelegramMessageHandler.__subclasses__():
        if subclass.message:
            handlers[subclass.message] = subclass(bot)

    return handlers


def register_callback_handlers():
    handlers = {}
    for subclass in BaseTelegramCallbackHandler.__subclasses__():
        if subclass.callback:
            handlers[subclass.callback] = subclass(bot)

    return handlers


def register_command_handlers():
    handlers = {}
    for subclass in BaseTelegramCommandHandler.__subclasses__():
        if subclass.command:
            handlers[subclass.command] = subclass(bot)

    return handlers
