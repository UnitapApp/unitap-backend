from telegram.bot import BaseTelegramMessageHandler, BaseTelegramCallbackHandler
from telebot import types
from django.conf import settings


class BugReportHandler(BaseTelegramMessageHandler):
    message = "Report a bug 🪲"

    def handler(self, message: types.Message):
        if self.get_user(message.from_user.id) is None:
            self.messenger.reply_to(
                message, text="Please connect your unitap account first"
            )

            return

        self.messenger.reply_to(message, text="Please describe the bug in detail.")

        self.register_next_step_handler(message, self.ask_for_bug_details)

    def ask_for_bug_details(self, message: types.Message):
        user_bug_details = message.text
        self.messenger.reply_to(
            message, text="How did the bug occur? Describe the steps."
        )

        # Save bug details and move to the next step (asking for how the bug occurred)
        self.register_next_step_handler(
            message, self.ask_for_bug_occurence, user_bug_details
        )

    def ask_for_bug_occurence(self, message: types.Message, user_bug_details):
        bug_occurence_details = message.text

        self.messenger.reply_to(
            message,
            text="Please upload an image related to the bug (optional, or send an empty message).",
        )
        # Save the bug occurrence details and ask for an image
        self.register_next_step_handler(
            message, self.collect_image, user_bug_details, bug_occurence_details
        )

    def collect_image(
        self, message: types.Message, user_bug_details, bug_occurence_details
    ):
        image = message.photo[-1].file_id if message.photo else None
        self.forward_to_private_channel(
            message, user_bug_details, bug_occurence_details, image
        )

        self.messenger.reply_to(
            message,
            text="Thank you for providing the information required for us to track the bug down\nWe will investigate and check back to you if the bug is valid and reward you with 1 extra chance at prizetap raffles",
        )

    # Step 3: Forward the bug report to a private channel with reward button
    def forward_to_private_channel(
        self, message: types.Message, user_bug_details, bug_occurence_details, image
    ):
        private_channel_id = (
            settings.TELEGRAM_BUG_REPORTER_CHANNEL_ID
        )  # Make sure this is set in Django settings

        # Construct message to forward to the private channel
        bug_report_message = (
            f"*Bug Report*\n"
            f"User Id: {message.from_user.id}\n"
            f"From: @{message.chat.username}\n\n"
            f"*Bug Description:* {user_bug_details}\n"
            f"*Steps to Reproduce:* {bug_occurence_details}\n\n"
            f"Unitap user id {self.get_user(message.from_user.id).pk}"
        )

        # Forward the text and image if provided
        if image:
            self.messenger.send_photo(
                chat_id=private_channel_id,
                photo=image,
                caption=bug_report_message,
                parse_mode="MarkdownV2",
            )
        else:
            self.messenger.send_message(
                chat_id=private_channel_id,
                text=bug_report_message,
                parse_mode="MarkdownV2",
            )

        reward_button = types.InlineKeyboardMarkup()
        reward_button.add(
            types.InlineKeyboardButton(
                text="Reward User", callback_data=f"reward_{message.chat.id}"
            )
        )

        self.messenger.send_message(
            chat_id=private_channel_id,
            text="Click below to reward this user:",
            reply_markup=reward_button,
        )


class ReportBugRewardHandler(BaseTelegramCallbackHandler):
    callback = "reward-bug"

    def handler(self, callback: types.CallbackQuery):
        user_id = next(self.params)

        user = self.get_user(user_id)

        user.prizetap_winning_chance_number += 1
        user.save()

        self.messenger.send_message(
            chat_id=user_id,
            text="Congraculations\n\nYou got 1 extra prizetap chance for reporting a valid bug ❤️❤️.",
        )
