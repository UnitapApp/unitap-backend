from django.db import models
from authentication.models import UserProfile
from core.models import UserConstraint
from django.utils import timezone


class Constraint(UserConstraint):
    pass


class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# the Mission class which is the main model of the app
class Mission(models.Model):
    title = models.CharField(max_length=200)
    creator_name = models.CharField(max_length=200, null=True, blank=True)
    creator_url = models.URLField(max_length=200, null=True, blank=True)
    discord_url = models.URLField(max_length=200, null=True, blank=True)
    twitter_url = models.URLField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    imageUrl = models.CharField(max_length=200, null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    constraints = models.ManyToManyField(
        Constraint, blank=True, related_name="missions"
    )
    constraint_params = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.title

    @property
    def total_XP(self):
        return self.stations.aggregate(total_XP=models.Sum("total_XP"))["total_XP"]


class Referral(models.Model):
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name="referrals"
    )
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="referrals_recieved"
    )
    referred_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, null=True, related_name="referals_made"
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return f"{self.profile} referred by {self.referred_by} for {self.mission}"


class Station(models.Model):
    class Meta:
        unique_together = (("mission", "order"),)
        ordering = ["order"]

    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name="stations"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    imageUrl = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.mission} - {self.title}"

    @property
    def total_XP(self):
        return self.tasks.aggregate(total_XP=models.Sum("XP"))["total_XP"]


class TaskTypes:
    ARTICLE = "article"
    VIDEO = "video"
    QUIZ = "quiz"

    types = [
        (ARTICLE, "Article"),
        (VIDEO, "Video"),
        (QUIZ, "Quiz"),
    ]


class Task(models.Model):
    class Meta:
        unique_together = (("mission", "station", "order"),)
        ordering = ["order"]

    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="tasks")
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    task_type = models.CharField(
        max_length=200, null=True, blank=True, choices=TaskTypes.types
    )
    description = models.TextField(null=True, blank=True)
    imageUrl = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    definition = models.TextField(null=True, blank=True)

    has_action = models.BooleanField(default=False)
    action_button_text = models.CharField(
        max_length=200, null=True, blank=True, default="Verify"
    )

    verifications = models.ManyToManyField(Constraint, blank=True)
    verifications_definition = models.TextField(null=True, blank=True)

    XP = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.station} - {self.title}"

    def is_last_task_of_the_station(self):
        return self.station.tasks.last() == self

    def is_first_task_of_the_station(self):
        return self.station.tasks.first() == self

    def is_first_task_of_the_mission(self):
        return self.mission.stations.first().tasks.first() == self

    def is_last_task_of_the_mission(self):
        return self.mission.stations.last().tasks.last() == self
