from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp.cloudflare import CloudflareUtil


import logging

from core.utils import RequestContextExtractor


logger = logging.getLogger(__name__)


class HasVerifiedCloudflareCaptcha(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value
    is_cachable = False

    def is_observed(self, *args, **kwargs) -> bool:

        context = kwargs.get("context")

        if context is None or context.get("request") is None:
            return False

        cloudflare = CloudflareUtil()

        request_context: RequestContextExtractor = RequestContextExtractor(
            context["request"]
        )

        turnstile_token = request_context.data.get("cf-turnstile-response")

        return request_context.ip is not None and turnstile_token is not None and cloudflare.is_verified(
            turnstile_token, request_context.ip
        )
