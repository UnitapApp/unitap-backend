

from django.http import HttpRequest
from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp.cloudflare import CloudflareUtil


import logging


logger = logging.getLogger(__name__)



class HasVerifiedCloudflareCaptcha(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value

    @staticmethod
    def get_client_ip(x_forwarded_for):
        if x_forwarded_for:
            ip_list = [ip.strip() for ip in x_forwarded_for.split(',')]
            for ip in ip_list:
                if ip and not ip.startswith(('10.', '172.16.', '192.168.')):
                    return ip
        return None


    def is_observed(self, *args, **kwargs) -> bool:
        cloudflare = CloudflareUtil()

        if self.context is None or self.context.get("request") is None:
            return False
        
        request = self.context["request"]

        turnstile_token = request.data.get("cf-turnstile-response") or request.query_params.get("cf-turnstile-response")

        return (
            turnstile_token is not None and 
            cloudflare.is_verified(
                turnstile_token, 
                self.get_client_ip(request.META.get('HTTP_X_FORWARDED_FOR') or request.META['REMOTE_ADDR']) # type: ignore
            )
        )
