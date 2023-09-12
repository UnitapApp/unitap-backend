import json
from rest_framework.exceptions import PermissionDenied
from authentication.models import UserProfile
from .models import Mission, Task
from .constraints import *


class TaskVerificationValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.task: Task = kwargs["task"]

    def verify_task(self):
        if not self.task.is_active:
            raise PermissionDenied("Can't verify task")

    def check_user_constraints(self):
        try:
            verification_definitions = json.loads(self.task.verifications_definition)
        except:
            verification_definitions = {}

        for verification in self.task.verifications.all():
            constraint: ConstraintVerification = eval(verification.name)(
                self.user_profile
            )
            constraint.response = verification.response
            try:
                constraint.set_param_values(verification_definitions[verification.name])
            except KeyError:
                pass
            if not constraint.is_observed(self.task.verifications_definition):
                raise PermissionDenied(constraint.response)

    def is_valid(self, data):
        self.verify_task()

        self.check_user_constraints()
