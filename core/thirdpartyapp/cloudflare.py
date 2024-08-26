import logging
from django.conf import settings
import requests


logger = logging.getLogger(__name__)


class CloudflareUtil:
    secret_key = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
    api_url = "https://challenges.cloudflare.com/turnstile/v0"

    def is_verified(self, token: str, ip: str) -> bool:
        try:
            res = requests.post(
                f"{self.api_url}/siteverify",
                data={"secret": self.secret_key, "response": token, "remoteip": ip},
            )

            return res.ok and res.json()["success"]
        except Exception as e:
            logger.info(f"Error occurred during cloudflare verification {str(e)}")

            return False
