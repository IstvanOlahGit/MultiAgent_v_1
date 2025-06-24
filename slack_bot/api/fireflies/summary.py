from typing import Dict, List

from langchain.prompts import PromptTemplate

from slack_bot.api.fireflies.prompt import transcription_prompts

from slack_bot.core.config import settings


chat = settings.LLM_MINI

claude_prompt = PromptTemplate(
    template=transcription_prompts.prompt,
    input_variables=["transcription"],
)

chain = claude_prompt | chat

async def generate_transcription_summary(transcription: List[Dict[str, str]]) -> str:
    response = await chain.ainvoke({"transcription": transcription})
    return response.content[0]["text"]
