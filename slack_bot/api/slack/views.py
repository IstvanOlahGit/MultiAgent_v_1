import asyncio
import base64
from typing import List

from fastapi import Request, UploadFile, File
from slack_bot.api.agent.agent import SlackAgent
from slack_bot.api.agent.db_requests import get_last_3_messages, get_message_history
from slack_bot.api.responses.dto import UploadingFile
from slack_bot.api.responses.responses import create_vector_store, upload_files
from slack_bot.api.slack import slack_router
from slack_bot.api.slack.utils import post_message, get_user_info
from slack_bot.api.tasks.model import CreateMessageRequest, MessageResponse
from slack_bot.core.config import settings
from slack_bot.core.wrappers import SlackResponseWrapper


processed_event_ids = set()
event_id_lock = asyncio.Lock()

@slack_router.post('')
async def slack_events(request: Request):
    body = await request.json()

    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}


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

    print(event)
    asyncio.create_task(remove_event_id_later(event_id))
    if (
            event.get("type") == "message" and
            "subtype" not in event and
            "bot_id" not in event
    ):
        user_msg = event.get("text")
        user_id = event.get("user")
        user_info = get_user_info(user_id)
        user_name = user_info.name
        channel_id = event.get("channel")

        last_3_msg = get_last_3_messages(channel_id),
        message_history = await get_message_history(channel_id)

        agent = SlackAgent(channel_id, last_3_msg, message_history, user_id, user_name)
        response = await agent.run(user_msg)
        await post_message(channel_id, response)


async def remove_event_id_later(event_id: str, delay: int = 300):
    await asyncio.sleep(delay)
    async with event_id_lock:
        processed_event_ids.discard(event_id)

#
# @slack_router.post('/')
# async def create_message(
#         message_data: CreateMessageRequest
# ) -> SlackResponseWrapper[MessageResponse]:
#     chat_id = 'C0923BVRB3K'
#     user_id = 'U08VBAS8413'
#     user_name = 'Istvan Olah 3'
#     message_history = await get_message_history(chat_id)
#     last_3_msg = get_last_3_messages(chat_id),
#     agent = SlackAgent(chat_id, last_3_msg, message_history, user_id, user_name)
#     response = await agent.run(message_data.text)
#     return SlackResponseWrapper(data=MessageResponse(text=response))


