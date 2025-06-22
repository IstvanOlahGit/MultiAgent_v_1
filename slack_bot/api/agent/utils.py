import asyncio

import httpx

from slack_bot.core.config import settings


def normalize_deadline_field(d):
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) and "$date" in value:
                d[key] = value["$date"]
            else:
                normalize_deadline_field(value)
    elif isinstance(d, list):
        for item in d:
            normalize_deadline_field(item)


async def send_verification_email(email: str, content: str) -> None:
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=15)) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json"
            },
            json={
                "sender": {
                    "email": "security@marscapita.com",
                    "name": "MarsCAPITA"
                },
                "to": [
                    {
                        "email": email,
                    }
                ],
                "subject": "Reminder",
                "textContent": content
            }
        )
        response.raise_for_status()

