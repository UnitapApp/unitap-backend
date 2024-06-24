import os
import urllib.parse

import requests

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
DISCORD_AUTH_URL = os.getenv("DISCORD_AUTH_URL")
DISCORD_TOKEN_URL = os.getenv("DISCORD_TOKEN_URL")
DISCORD_API_URL = os.getenv("DISCORD_API_URL")


class DiscordUtils:
    @staticmethod
    def get_authorization_url():
        params = {
            "client_id": DISCORD_CLIENT_ID,
            "redirect_uri": DISCORD_REDIRECT_URI,
            "response_type": "code",
            "scope": "identify guilds",
        }
        return f"{DISCORD_AUTH_URL}?{urllib.parse.urlencode(params)}"

    @staticmethod
    def get_tokens(code):
        data = {
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_REDIRECT_URI,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
        r.raise_for_status()
        tokens = r.json()
        return tokens["access_token"], tokens["refresh_token"]

    @staticmethod
    def get_user_info(access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"{DISCORD_API_URL}/users/@me", headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_user_guilds(access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"{DISCORD_API_URL}/users/@me/guilds", headers=headers)
        r.raise_for_status()
        return r.json()
