from django.conf import settings
import requests


class CloudflareUtil:
  def __init__(self) -> None:
    self.api_url = "https://challenges.cloudflare.com/turnstile/v0"
    self.secret_key = settings.CLOUDFLARE_TURNSITE_SECRET_KEY


  def is_verified(self, token: str, ip: str) -> bool:
    res = requests.post(
        f"{self.api_url}/siteverify",
        data={
            "secret": self.secret_key,
            "response": token,
            "remoteip": ip
        },
    )

    return res.ok and res.json()["success"]
