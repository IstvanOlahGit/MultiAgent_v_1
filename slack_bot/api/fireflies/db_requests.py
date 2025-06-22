from slack_bot.api.fireflies.model import TranscriptionModel
from slack_bot.core.config import settings


async def add_transcription_obj(transcription: TranscriptionModel):
    await settings.DB_CLIENT.transcriptions.insert_one(transcription.to_mongo())
