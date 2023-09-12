from rest_framework.test import APITestCase, override_settings
from django.urls import reverse
from .models import *
from django.utils import timezone
from authentication.models import NetworkTypes
from .constraints import *


class MissionModelAndAPITests(APITestCase):
    def setUp(self):
        self.profile = UserProfile.objects.get_or_create("mamad")
        self.tag1 = Tag.objects.create(name="test tag")
        self.tag2 = Tag.objects.create(name="test tag2")

        self.mission = Mission.objects.create(
            title="test mission",
            creator_name="mamad",
            creator_url="https://mamad.com",
            discord_url="https://discord.com",
            twitter_url="https://twitter.com",
            description="this is a test mission",
            imageUrl="https://mamad.com",
            is_promoted=True,
            is_active=True,
            constraint_params="{}",
        )
        self.mission.tags.add(self.tag1)
        self.mission.tags.add(self.tag2)

        self.mission.constraints.add(
            Constraint.objects.create(
                name=BrightIDAuraVerification.__name__,
                title="BrightID aura",
                description="You have to be Aura verified.",
            )
        )
        self.mission.save()

    def test_misison_creation(self):
        self.assertEqual(len(Mission.objects.all()), 1)
        mission = Mission.objects.first()

        self.assertEqual(mission.title, "test mission")
        self.assertEqual(mission.creator_name, "mamad")
        self.assertEqual(mission.creator_url, "https://mamad.com")
        self.assertEqual(mission.discord_url, "https://discord.com")
        self.assertEqual(mission.twitter_url, "https://twitter.com")
        self.assertEqual(mission.description, "this is a test mission")
        self.assertEqual(mission.imageUrl, "https://mamad.com")
        self.assertEqual(mission.is_promoted, True)
        self.assertEqual(mission.is_active, True)
        self.assertEqual(mission.constraint_params, "{}")
        self.assertEqual(mission.constraints.count(), 1)
        self.assertEqual(mission.tags.count(), 2)

    def test_mission_api(self):
        url = reverse("mission-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        mission = response.data[0]
        self.assertEqual(mission["title"], "test mission")
        self.assertEqual(mission["creator_name"], "mamad")
        self.assertEqual(mission["creator_url"], "https://mamad.com")
        self.assertEqual(mission["discord_url"], "https://discord.com")
        self.assertEqual(mission["twitter_url"], "https://twitter.com")
        self.assertEqual(mission["description"], "this is a test mission")
        self.assertEqual(mission["imageUrl"], "https://mamad.com")
        self.assertEqual(mission["is_promoted"], True)
        self.assertEqual(mission["is_active"], True)
        self.assertEqual(mission["constraint_params"], "{}")
        self.assertEqual(len(mission["constraints"]), 1)
        self.assertEqual(len(mission["tags"]), 2)


class referralTests(APITestCase):
    def setUp(self):
        self.profile1 = UserProfile.objects.get_or_create("mamad")
        self.profile2 = UserProfile.objects.get_or_create("amir")

        self.mission = Mission.objects.create(
            title="test mission",
            creator_name="mamad",
            creator_url="https://mamad.com",
            discord_url="https://discord.com",
            twitter_url="https://twitter.com",
            description="this is a test mission",
            imageUrl="https://mamad.com",
            is_promoted=True,
            is_active=True,
            constraint_params="{}",
        )

    def test_referral_creation(self):
        Referral.objects.create(
            mission=self.mission,
            profile=self.profile1,
            referred_by=self.profile2,
        )
        self.assertEqual(len(Referral.objects.all()), 1)
        referral = Referral.objects.first()

        self.assertEqual(referral.mission, self.mission)
        self.assertEqual(referral.profile, self.profile1)
        self.assertEqual(referral.referred_by, self.profile2)

        self.assertEqual(len(self.profile1.referrals_recieved.all()), 1)
        self.assertEqual(len(self.profile2.referals_made.all()), 1)

    # referral list for a user
    # def test_referral_api(self):
    #     url = reverse("referral-list")
    #     self.client.force_login(self.profile1)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data), 0)

    #     referral.objects.create(
    #         mission=self.mission,
    #         profile=self.profile1,
    #         referred_by=self.profile2,
    #     )
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data), 1)
    #     self.assertEqual


class TaskAPITest(APITestCase):
    def setUp(self):
        self.profile1 = UserProfile.objects.get_or_create("mamad")

        self.mission = Mission.objects.create(
            title="test mission",
            creator_name="mamad",
            creator_url="https://mamad.com",
            discord_url="https://discord.com",
            twitter_url="https://twitter.com",
            description="this is a test mission",
            imageUrl="https://mamad.com",
            is_promoted=True,
            is_active=True,
            constraint_params="{}",
        )

        self.station1 = Station.objects.create(
            mission=self.mission,
            title="test station1",
            description="this is a test station",
            imageUrl="https://mamad.com",
            is_active=True,
            order=0,
        )
        self.station2 = Station.objects.create(
            mission=self.mission,
            title="test station2",
            description="this is a test station",
            imageUrl="https://mamad.com",
            is_active=True,
            order=1,
        )
        self.task1 = Task.objects.create(
            mission=self.mission,
            station=self.station1,
            title="test task1",
            description="this is a test task",
            imageUrl="https://mamad.com",
            is_active=True,
            order=0,
            has_action=True,
            action_button_text="test action",
            definition="{}",
            verifications_definition="{}",
            XP=100,
        )
        self.task2 = Task.objects.create(
            mission=self.mission,
            station=self.station1,
            title="test task2",
            description="this is a test task",
            imageUrl="https://mamad.com",
            is_active=True,
            order=1,
            has_action=True,
            action_button_text="test action",
            definition="{}",
            verifications_definition="{}",
            XP=10,
        )
        self.task3 = Task.objects.create(
            mission=self.mission,
            station=self.station2,
            title="test task3",
            description="this is a test task",
            imageUrl="https://mamad.com",
            is_active=True,
            order=0,
            has_action=True,
            action_button_text="test action",
            definition="{}",
            verifications_definition="{}",
            XP=40,
        )

    def test_task_creation(self):
        self.assertEqual(len(Mission.objects.all()), 1)
        self.assertEqual(len(Station.objects.all()), 2)
        self.assertEqual(len(Task.objects.all()), 3)

        mission: Mission = Mission.objects.first()
        self.assertEqual(mission, self.mission)
        self.assertEqual(mission.stations.count(), 2)
        self.assertEqual(mission.tasks.count(), 3)
        self.assertEqual(mission.stations.first(), self.station1)
        self.assertEqual(mission.stations.last(), self.station2)
        self.assertEqual(mission.first_task(), self.task1)
        self.assertEqual(mission.last_task(), self.task3)
        self.assertEqual(mission.stations.first().tasks.count(), 2)
        self.assertEqual(mission.stations.first().tasks.last(), self.task2)

        self.assertEqual(mission.stations.first().tasks.first().XP, 100)
        self.assertEqual(mission.stations.first().tasks.last().XP, 10)
        self.assertEqual(mission.stations.last().tasks.first().XP, 40)
        self.assertEqual(mission.stations.first().total_XP, 110)
        self.assertEqual(mission.stations.last().total_XP, 40)
        self.assertEqual(mission.total_XP, 150)

        self.assertTrue(
            mission.stations.first().tasks.first().is_first_task_of_the_station()
        )
        self.assertTrue(
            mission.stations.first().tasks.first().is_first_task_of_the_mission()
        )
        self.assertFalse(
            mission.stations.first().tasks.first().is_last_task_of_the_station()
        )
        self.assertFalse(
            mission.stations.first().tasks.last().is_first_task_of_the_station()
        )
        self.assertFalse(
            mission.stations.first().tasks.last().is_first_task_of_the_mission()
        )
        self.assertTrue(
            mission.stations.first().tasks.last().is_last_task_of_the_station()
        )
        self.assertTrue(
            mission.stations.last().tasks.first().is_first_task_of_the_station()
        )
        self.assertFalse(
            mission.stations.last().tasks.first().is_first_task_of_the_mission()
        )
        self.assertTrue(
            mission.stations.last().tasks.last().is_last_task_of_the_station()
        )
        self.assertTrue(
            mission.stations.last().tasks.last().is_last_task_of_the_mission()
        )
