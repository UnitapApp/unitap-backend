from telegram.bot import BaseTelegramMessageHandler, BaseTelegramCallbackHandler
from telebot import types
from django.conf import settings


class BugReportHandler(BaseTelegramMessageHandler):
    message = "Report a bug 🪲"

    def handler(self, message: types.Message):
        # Check if the user's Telegram account is linked to Unitap
        if self.get_user(message.from_user.id) is None:
            self.messenger.reply_to(
                message,
                text=(
                    "❌ *Your Telegram account is not connected to Unitap.*\n\n"
                    "To report a bug, please first connect your Telegram account to Unitap. "
                    "Visit the following link and log in: https://unitap.app. "
                    "Go to your profile and connect your Telegram account.\n\n"
                    "Once connected, you can report issues and help improve our platform. 😊"
                ),
                parse_mode="Markdown",
            )
            return

        # If the user is connected, start the bug reporting process
        self.messenger.reply_to(
            message,
            text=(
                "🪲 *Let's start with your bug report!*\n\n"
                "Please describe the issue you're facing in detail.\n"
                "_Try to include as much information as possible, such as what you were doing, what you expected to happen, and what actually happened._"
            ),
            parse_mode="Markdown",
        )
        self.register_next_step_handler(message, self.ask_for_bug_details)

    def ask_for_bug_details(self, message: types.Message):
        user_bug_details = message.text
        self.messenger.reply_to(
            message,
            text=(
                "🔄 *Got it! Now, please describe how the bug occurred.*\n\n"
                "_What were the steps you took that led to this issue?_ "
                "This will help us replicate the problem and find a fix more quickly."
            ),
            parse_mode="Markdown",
        )
        # Save bug details and move to the next step (asking for how the bug occurred)
        self.register_next_step_handler(
            message, self.ask_for_bug_occurence, user_bug_details
        )

    def ask_for_bug_occurence(self, message: types.Message, user_bug_details):
        bug_occurence_details = message.text

        self.messenger.reply_to(
            message,
            text=(
                "📸 *Almost done!*\n\n"
                "If you have any screenshots or images that can help us better understand the issue, "
                "please upload them now.\n"
                "_If you don't have any images, just send an empty message._"
            ),
            parse_mode="Markdown",
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
            text=(
                "✅ *Thank you for providing all the necessary details!*\n\n"
                "We will review your report and investigate the issue. "
                "If your report is valid, you will be rewarded with an *extra chance* in our Prizetap raffles 🎉.\n\n"
                "_We truly appreciate your efforts in making Unitap a better platform!_"
            ),
            parse_mode="Markdown",
        )

    # Step 3: Forward the bug report to a private channel with reward button
    def forward_to_private_channel(
        self, message: types.Message, user_bug_details, bug_occurence_details, image
    ):
        private_channel_id = (
            settings.TELEGRAM_BUG_REPORTER_CHANNEL_ID
        )  # Ensure this is set in Django settings

        if not private_channel_id:
            return

        # Construct message to forward to the private channel
        bug_report_message = (
            f"*New Bug Report*\n"
            f"👤 *User:* @{message.chat.username} (ID: {message.from_user.id})\n"
            f"Unitap User ID: {self.get_user(message.from_user.id).pk}\n\n"
            f"*Bug Description:* {user_bug_details}\n"
            f"*Steps to Reproduce:* {bug_occurence_details}\n\n"
            "-----------------------------------"
        )

        # Forward the text and image if provided
        if image:
            forwarded_message = self.messenger.send_photo(
                chat_id=private_channel_id,
                photo=image,
                caption=bug_report_message,
                parse_mode="MarkdownV2",
            )
        else:
            forwarded_message = self.messenger.send_message(
                chat_id=private_channel_id,
                text=bug_report_message,
                parse_mode="MarkdownV2",
            )

        reward_button = types.InlineKeyboardMarkup()
        reward_button.add(
            types.InlineKeyboardButton(
                text="Reward User 🏆",
                callback_data=self.messenger.build_callback_string(
                    "reward-bug", [message.from_user.id]
                ),
            )
        )

        # Send the forwarded message with the reward button in the private channel
        self.messenger.reply_to(
            forwarded_message,
            text="Click below to reward this user:",
            reply_markup=reward_button,
        )


class ReportBugRewardHandler(BaseTelegramCallbackHandler):
    callback = "reward-bug"

    def handler(self, callback: types.CallbackQuery):
        user_id = int(self.params[0])

        # Retrieve the user and increment their prize chances
        user = self.get_user(user_id)
        user.prizetap_winning_chance_number += 1
        user.save()

        # Update the message in the private channel to indicate the user has been rewarded
        self.messenger.update_query_messages(
            callback, "User rewarded ✅", reply_markup=types.InlineKeyboardMarkup()
        )

        # Notify the user that they have received the reward
        self.messenger.send_message(
            chat_id=user_id,
            text=(
                "🎉 *Congratulations!*\n\n"
                "Your bug report has been validated, and you’ve been rewarded with an *extra chance* "
                "in the Prizetap raffles 🎟️.\n\n"
                "Thank you for helping us improve Unitap! 💪"
            ),
            parse_mode="Markdown",
        )
