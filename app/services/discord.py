import requests
from app.config import Config


def send_webhook_discord_message(msg: str) -> None:
    data = {
        "content": msg
    }

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(Config.DISCORD_WEBHOOK_URL, headers=headers, data=data)
