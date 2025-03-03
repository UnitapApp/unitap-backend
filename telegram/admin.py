# admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import TelegramConnection
from .forms import BroadcastMessageForm
from telegram.bot import TelegramMessenger
from django.core.exceptions import PermissionDenied


@admin.register(TelegramConnection)
class TelegramConnectionAdmin(admin.ModelAdmin):
    list_display = ("pk", "user_profile", "user_id")  # Adjust as per your model fields

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "broadcast/",
                self.admin_site.admin_view(self.broadcast_view),
                name="broadcast_message",
            ),
        ]
        return custom_urls + urls

    @admin.action(
        description="Broadcast message to all users",
        permissions=["telegram.can_broadcast"],
    )
    def broadcast_view(self, request):
        if not request.user.has_perm("telegram.can_broadcast"):
            raise PermissionDenied("You do not have permission to broadcast messages.")

        if request.method == "POST":
            form = BroadcastMessageForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data["message"]
                users = TelegramConnection.objects.all()
                messenger = TelegramMessenger.get_instance()
                for user in users:
                    messenger.send_message(user.user_id, text=message)

                self.message_user(request, "Message sent to all users!")
                return render(request, "admin/broadcast.html", {"form": form})
        else:
            form = BroadcastMessageForm()

        return render(request, "admin/broadcast.html", {"form": form})
