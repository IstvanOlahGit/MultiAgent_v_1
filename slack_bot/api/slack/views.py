from fastapi import Request

from slack_bot.api.slack import slack_router
from slack_bot.api.slack.utils import post_message


@slack_router.post('')
async def slack_events(request: Request):
    body = await request.json()

    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    if body.get("type") == "event_callback":
        event = body["event"]
        if event.get("type") == "app_mention" and "bot_id" not in event:
            user_msg = event.get("text")
            user = event.get("user")
            channel = event.get("channel")

            if "отчет" in user_msg.lower():
                await post_message(channel, f"<@{user}>, вот ссылка на гугл-док: https://docs.google.com/...")

    return {"ok": True}