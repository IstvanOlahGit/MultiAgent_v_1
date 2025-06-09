from fastapi import Request

from slack_bot.api.agent.agent import SlackAgent
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
            channel = event.get("channel")

            agent = SlackAgent(channel)
            response = await agent.run(user_msg)
            await post_message(channel, response)

    return {"ok": True}