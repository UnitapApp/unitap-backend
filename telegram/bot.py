import telebot
from django.conf import settings


bot = telebot.TeleBot(settings.TELEGRAM_BOT_API_KEY)
