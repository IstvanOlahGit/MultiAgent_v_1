import httpx

from slack_bot.core.config import settings


async def post_message(channel, text):
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": text}
        )