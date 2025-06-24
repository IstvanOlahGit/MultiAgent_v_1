from functools import lru_cache


class TranscriptionPrompt:
    prompt = """You are an assistant that summarizes business or support-related phone calls. Below is the full transcription of a call.

Your task is to write a concise, clear summary of the call in 2-4 sentences. Focus on the main points discussed, any decisions made, key people mentioned, and any follow-up actions. Do not include small talk or filler content.

Transcription:
{transcription}"""


@lru_cache()
def get_prompts() -> TranscriptionPrompt:
    return TranscriptionPrompt()


transcription_prompts = get_prompts()
