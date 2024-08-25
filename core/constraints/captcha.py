

from django.http import HttpRequest
from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp.cloudflare import CloudflareUtil


import logging

from core.utils import RequestContextExtractor


logger = logging.getLogger(__name__)



class HasVerifiedCloudflareCaptcha(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value


    def is_observed(self, *args, **kwargs) -> bool:
        cloudflare = CloudflareUtil()

        if self.context is None or self.context.get("request") is None:
            return False
        
        request: RequestContextExtractor = self.context["request"]

        turnstile_token = request.data.get("cf-turnstile-response")

        return (
            turnstile_token is not None and 
            cloudflare.is_verified(
                turnstile_token, 
                self.get_client_ip(request.ip) # type: ignore
            )
        )
