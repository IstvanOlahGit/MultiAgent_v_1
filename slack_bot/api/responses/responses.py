import asyncio
import io
import base64

from slack_bot.api.responses.dto import UploadingFile
from slack_bot.api.responses.prompt import responses_prompts
from slack_bot.core.config import settings


async def generate_answer(
    query: str,
) -> str | bool:
    prompt = responses_prompts.prompt.format(query=query)
    response = await settings.OPENAI_CLIENT.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [settings.VECTOR_STORE_ID]
        }]
    )
    return response.output_text


async def create_vector_store() -> str:
    vector_store = await settings.OPENAI_CLIENT.vector_stores.create()
    return vector_store.id


async def upload_files(vs_id: str, files: list[UploadingFile]) -> None:
    await asyncio.gather(*[
        settings.OPENAI_CLIENT.vector_stores.files.upload_and_poll(
            vector_store_id=vs_id,
            file=(file.name, io.BytesIO(base64.b64decode(file.base64String)))
        ) for file in files
    ])


async def upload_file(vs_id: str, file: UploadingFile) -> None:
    await settings.OPENAI_CLIENT.vector_stores.files.upload_and_poll(
            vector_store_id=vs_id,
            file=(file.name, io.BytesIO(base64.b64decode(file.base64String)))
        )


