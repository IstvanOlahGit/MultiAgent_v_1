from datetime import datetime

from pydantic import BaseModel

from slack_bot.core.database import MongoBaseModel


class TaskModel(MongoBaseModel):
    user_id: str
    description: str
    deadline: datetime


class CreateMessageRequest(BaseModel):
    text: str


class MessageResponse(BaseModel):
    text: str