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
        return sum([station.total_XP for station in self.stations.all()])

    def first_task(self):
        return self.stations.first().tasks.first()

    def last_task(self):
        return self.stations.last().tasks.last()


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

    def get_next_task(self):
        if self.is_last_task_of_the_station():
            if self.is_last_task_of_the_mission():
                return None
            else:
                return self.mission.stations.get(
                    order=self.station.order + 1
                ).tasks.first()
        else:
            return self.station.tasks.get(order=self.order + 1)

    def get_previous_task(self):
        if self.is_first_task_of_the_station():
            if self.is_first_task_of_the_mission():
                return None
            else:
                return self.mission.stations.get(
                    order=self.station.order - 1
                ).tasks.last()
        else:
            return self.station.tasks.get(order=self.order - 1)


class UserMissionProgress(models.Model):
    class Meta:
        unique_together = (("profile", "mission"),)

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    current_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True, editable=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.profile} - {self.mission} - {self.is_completed}"


class UserTaskProgress(models.Model):
    class Meta:
        unique_together = (("profile", "task"),)

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    user_data = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.profile} - {self.task} - {self.is_completed}"
