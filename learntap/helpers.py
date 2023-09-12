from .models import *


class UserProgressManager:
    @classmethod
    def start_mission(cls, profile: UserProfile, mission: Mission):
        task = mission.stations.first().tasks.first()
        UserMissionProgress.objects.get_or_create(
            profile=profile,
            mission=mission,
            current_task=task,
        )
        UserTaskProgress.objects.get_or_create(profile=profile, task=task)

    @classmethod
    def update_user_progress(cls, profile: UserProfile, task: Task):
        # update user task progress
        user_task_progress = UserTaskProgress.objects.get_or_create(
            profile=profile, task=task
        )[0]
        user_task_progress.is_completed = True
        user_task_progress.completed_at = timezone.now()
        user_task_progress.save()

        # update user mission progress
        user_mission_progress = UserMissionProgress.objects.get_or_create(
            profile=profile, mission=task.mission
        )[0]

        if task.is_last_task_of_the_mission():
            user_mission_progress.current_task = None
            user_mission_progress.is_completed = True
            user_mission_progress.completed_at = timezone.now()
            user_mission_progress.save()
            return

        user_mission_progress.current_task = task.get_next_task()
        user_mission_progress.save()

    @classmethod
    def get_current_task_of_mission(
        cls, profile: UserProfile, mission: Mission
    ) -> Task:
        return UserMissionProgress.objects.get(
            profile=profile, mission=mission
        ).current_task

    @classmethod
    def has_completed_mission(cls, profile: UserProfile, mission: Mission) -> bool:
        return UserMissionProgress.objects.filter(
            profile=profile, mission=mission, is_completed=True
        ).exists()

    @classmethod
    def has_completed_task(cls, profile: UserProfile, task: Task) -> bool:
        return UserTaskProgress.objects.filter(
            profile=profile, task=task, is_completed=True
        ).exists()

    @classmethod
    def get_user_mission_progress(
        cls, profile: UserProfile, mission: Mission
    ) -> UserMissionProgress:
        return UserMissionProgress.objects.get(profile=profile, mission=mission)

    @classmethod
    def get_user_mission_progress_percentage(
        cls, profile: UserProfile, mission: Mission
    ) -> int:
        number_of_tasks_in_mission = mission.tasks.all().count()
        number_of_completed_tasks = UserTaskProgress.objects.filter(
            profile=profile, task__mission=mission, is_completed=True
        ).count()
        return int(number_of_completed_tasks / number_of_tasks_in_mission * 100)

    @classmethod
    def has_started_mission(cls, profile: UserProfile, mission: Mission) -> bool:
        return UserMissionProgress.objects.filter(
            profile=profile, mission=mission, is_completed=False
        ).exists()

    @classmethod
    def get_user_task_progress(
        cls, profile: UserProfile, task: Task
    ) -> UserTaskProgress:
        return UserTaskProgress.objects.get(profile=profile, task=task)

    @classmethod
    def get_user_mission_progresses(cls, profile: UserProfile) -> [UserMissionProgress]:
        return UserMissionProgress.objects.filter(profile=profile)

    @classmethod
    def get_user_task_progresses(cls, profile: UserProfile) -> [UserTaskProgress]:
        return UserTaskProgress.objects.filter(profile=profile)
