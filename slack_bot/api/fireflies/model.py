from typing import List, Dict

from slack_bot.core.database import MongoBaseModel


class TranscriptionModel(MongoBaseModel):
    dateString: str
    users: List[str]
    transcription: List[Dict[str, str]]