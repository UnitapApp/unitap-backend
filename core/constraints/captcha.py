

from django.http import HttpRequest
from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp.cloudflare import CloudflareUtil


import logging


logger = logging.getLogger(__name__)



class HasVerifiedCloudflareCaptcha(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        return (
            x_forwarded_for.split(',')[0]
            if (x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'))
            else request.META['REMOTE_ADDR']
        )

    def is_observed(self, *args, **kwargs) -> bool:
        cloudflare = CloudflareUtil()

        if self.context is None or self.context.get("request") is None:
            return False
        
        request = self.context["request"]

        token = request.data.get("cf-turnstile-response") or request.query_params.get("cf-turnstile-response")


        if not token:
            return False

        return cloudflare.is_verified(token, self.get_client_ip(request))
