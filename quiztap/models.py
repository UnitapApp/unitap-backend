from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication.models import UserProfile
from core.models import BigNumField, Chain

# Create your models here.


class Competition(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", _("Not started")
        IN_PROGRESS = "IN_PROGRESS", _("In progress")
        FINISHED = "FINISHED", _("Finished")

    title = models.CharField(max_length=255)
    sponsor = models.CharField(max_length=127, blank=True, null=True)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="held_competitions"
    )
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(null=False, blank=False)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOT_STARTED
    )
    prize_amount = BigNumField(null=False, blank=False)
    chain = models.ForeignKey(
        Chain,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="competitions",
    )
    token = models.CharField(max_length=100)
    token_address = models.CharField(max_length=255)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    email_url = models.EmailField(max_length=255)
    telegram_url = models.URLField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    token_image_url = models.URLField(max_length=255, null=True, blank=True)

    participants = models.ManyToManyField(
        UserProfile, through="UserCompetition", related_name="participated_competitions"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.details


class UserCompetition(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    is_winner = models.BooleanField(default=False)
    amount_won = BigNumField(null=True, blank=True)

    class Meta:
        unique_together = ("user_profile", "competition")


class Question(models.Model):
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="questions"
    )
    number = models.IntegerField(
        null=False, blank=False, validators=[MinValueValidator(1)]
    )
    can_be_shown = models.BooleanField(default=False, null=False, blank=False)
    answer_can_be_shown = models.BooleanField(default=False, null=False, blank=False)
    text = models.TextField()

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ("competition", "number")


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    user_competition = models.ForeignKey(
        UserCompetition,
        on_delete=models.CASCADE,
        related_name="users_answer",
        null=False,
        blank=False,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="users_answer",
        null=False,
        blank=False,
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name="users_answer",
        null=False,
        blank=False,
    )

    class Meta:
        unique_together = ("user_competition", "question")
