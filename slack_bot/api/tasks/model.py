from datetime import datetime

from slack_bot.core.database import MongoBaseModel


class TaskModel(MongoBaseModel):
    user_id: str
    description: str
    deadline: datetime