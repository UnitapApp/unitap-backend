from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp.cloudflare import CloudflareUtil


import logging

from core.utils import RequestContextExtractor


logger = logging.getLogger(__name__)


class HasVerifiedCloudflareCaptcha(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value

    def is_observed(self, *args, **kwargs) -> bool:

        if self.context is None or self.context.get("requset") is None:
            return False

        cloudflare = CloudflareUtil()

        request_context: RequestContextExtractor = RequestContextExtractor(
            self.context["requset"]
        )

        turnstile_token = request_context.data.get("cf-turnstile-response")

        return turnstile_token is not None and cloudflare.is_verified(
            turnstile_token, request_context.ip
        )
