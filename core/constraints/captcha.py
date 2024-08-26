from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp.cloudflare import CloudflareUtil


import logging

from core.utils import RequestContextExtractor


logger = logging.getLogger(__name__)


class HasVerifiedCloudflareCaptcha(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value

    def is_observed(self, *args, **kwargs) -> bool:

        if self.context is None or self.context.get("request_context") is None:
            return False

        cloudflare = CloudflareUtil()

        request: RequestContextExtractor = RequestContextExtractor(
            self.context["request_context"]
        )

        turnstile_token = request.data.get("cf-turnstile-response")

        return turnstile_token is not None and cloudflare.is_verified(
            turnstile_token, request.ip
        )
