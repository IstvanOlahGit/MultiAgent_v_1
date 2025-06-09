import asyncio
from fastapi import Request
from slack_bot.api.agent.agent import SlackAgent
from slack_bot.api.slack import slack_router
from slack_bot.api.slack.utils import post_message

processed_event_ids = set()
event_id_lock = asyncio.Lock()

@slack_router.post('')
async def slack_events(request: Request):
    body = await request.json()

    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    # 2. Основная логика: запускаем в фоне
    if body.get("type") == "event_callback":
        asyncio.create_task(process_event(body))

    return {"ok": True}


async def process_event(body: dict):
    event = body["event"]
    event_id = body.get("event_id")

    async with event_id_lock:
        if event_id in processed_event_ids:
            return
        processed_event_ids.add(event_id)

    asyncio.create_task(remove_event_id_later(event_id))

    if event.get("type") == "app_mention" and "bot_id" not in event:
        user_msg = event.get("text")
        channel = event.get("channel")

        agent = SlackAgent(channel)
        response = await agent.run(user_msg)
        await post_message(channel, response)


async def remove_event_id_later(event_id: str, delay: int = 300):
    await asyncio.sleep(delay)
    async with event_id_lock:
        processed_event_ids.discard(event_id)
