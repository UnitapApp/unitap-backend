from django.core.validators import MinValueValidator
from django.db import models

from authentication.models import UserProfile
from core.models import BigNumField, Chain

# Create your models here.


class Competition(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("holding", "Holding"),
        ("finished", "Finished"),
    ]

    sponsor = models.CharField(max_length=127, blank=True, null=True)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="held_competitions"
    )
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(null=False, blank=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
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
    rest_time_seconds = models.IntegerField(
        default=5, validators=[MinValueValidator(5)]
    )
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


class Question(models.Model):
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="questions"
    )
    number = models.IntegerField(
        null=False, blank=False, validators=[MinValueValidator(1)]
    )
    answer_time_limit_seconds = models.IntegerField(
        default=10, validators=[MinValueValidator(5)]
    )
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
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="user_answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="user_answers"
    )
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.CASCADE, related_name="user_answers"
    )
