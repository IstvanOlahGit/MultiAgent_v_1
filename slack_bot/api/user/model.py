from pydantic import BaseModel


class SlackUserModel(BaseModel):
    position: str | None
    name: str
    employee_id: str
    email: str | None

