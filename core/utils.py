import datetime
import pytz
from time import time
from django.utils import timezone

class TimeUtils:

    @staticmethod
    def get_last_monday():
        now = int(time())
        day = 86400  # seconds in a day
        week = 7 * day
        weeks = now // week  # number of weeks since epoch
        monday = 345600  # first monday midnight
        last_monday_midnight = monday + (weeks * week)

        # last monday could be off by one week
        if last_monday_midnight > now:
            last_monday_midnight -= week

        return timezone.make_aware(
            datetime.datetime.fromtimestamp(last_monday_midnight)
        )
    
    @staticmethod
    def get_second_last_monday():
        now = int(time())
        day = 86400  # seconds in a day
        week = 7 * day
        weeks = now // week  # number of weeks since epoch
        monday = 345600  # first monday midnight
        last_monday_midnight = monday + (weeks * week)

        # last monday could be off by one week
        if last_monday_midnight > now:
            last_monday_midnight -= week

        return timezone.make_aware(
            datetime.datetime.fromtimestamp(last_monday_midnight - week)
        )

    @staticmethod
    def get_first_day_of_the_month():
        now = datetime.datetime.now(pytz.timezone("UTC"))
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_day