import logging

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintVerification,
)


logger = logging.getLogger(__name__)


class HasTelegramConnection(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value

    def is_observed(self, *args, **kwargs) -> bool:
        from telegram.models import TelegramConnection

        try:
            twitter = TelegramConnection.get_connection(self.user_profile)
        except TelegramConnection.DoesNotExist:
            return False
        return twitter.is_connected()
