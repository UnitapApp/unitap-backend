import logging
from django.conf import settings
import requests


logger = logging.getLogger(__name__)


class HCaptchaUtil:
    secret_key = settings.H_CAPTCHA_SECRET
    api_url = "https://api.hcaptcha.com"

    def is_verified(self, token: str, ip: str) -> bool:
        try:
            res = requests.post(
                f"{self.api_url}/siteverify",
                data={"secret": self.secret_key, "response": token, "remoteip": ip},
            )

            return res.ok and res.json()["success"]
        except Exception as e:
            logger.info(f"Error occurred during hcaptcha verification {str(e)}")

            return False
