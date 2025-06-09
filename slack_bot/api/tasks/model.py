from datetime import datetime

from pydantic import Field

from slack_bot.core.database import MongoBaseModel


class TaskModel(MongoBaseModel):
    user_id: str
    description: str
    deadline: datetime