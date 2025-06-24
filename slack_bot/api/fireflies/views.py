import asyncio

from fastapi import Request

from slack_bot.api.fireflies import fireflies_router
from slack_bot.api.fireflies.db_requests import add_transcription_obj
from slack_bot.api.fireflies.summary import generate_transcription_summary
from slack_bot.api.fireflies.utils import get_call_transcription, parse_conversation, delete_call_transcription, \
    post_call_transcripton


@fireflies_router.post("/call/report")
async def add_transcription(
        request: Request,
):
    payload = await request.json()
    transcription_id = payload['meetingId']
    transcription_data = await get_call_transcription(transcription_id)
    transcription_model = parse_conversation(transcription_data)
    summary = await generate_transcription_summary(transcription_model.transcription)
    transcription_model = await add_transcription_obj(transcription_model, summary)
    await post_call_transcripton(transcription_model)
