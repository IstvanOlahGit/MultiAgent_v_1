from fastapi import Request

from slack_bot.api.fireflies import fireflies_router
from slack_bot.api.fireflies.utils import get_call_transcription


@fireflies_router.post("/call/report")
async def get_call_report_original(
    request: Request,
):
    payload = await request.json()
    transcription_id = payload['meetingId']
    transcription_data = await get_call_transcription(transcription_id)
    print(transcription_data)
