from pydantic import BaseModel


class HumanMessageModel(BaseModel):
    content: str


class AIMessageModel(BaseModel):
    content: str