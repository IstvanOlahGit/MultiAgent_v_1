from pydantic import BaseModel, Field


class UploadingFile(BaseModel):
    name: str
    base64String: str | None = Field(exclude=True, default=None)