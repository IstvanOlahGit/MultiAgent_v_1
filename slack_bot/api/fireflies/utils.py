import asyncio
from datetime import datetime

import httpx

from slack_bot.api.fireflies.model import TranscriptionModel
from slack_bot.api.slack.utils import post_message
from slack_bot.core.config import settings


async def get_call_transcription(transcription_id: str):
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=20)) as client:
        query = '''
            query Transcript($transcriptId: String!) {
              transcript(id: $transcriptId) {
                title
                dateString
                user {
                  email
                  name
                }
                duration
                video_url
                audio_url
                sentences {
                  speaker_name
                  text
                }
              }
            }
            '''
        data = {
            'query': query,
            'variables': {'transcriptId': transcription_id}
        }
        response = await client.post("https://api.fireflies.ai/graphql",
                                     json=data,
                                     headers={"Authorization": f"Bearer {settings.FIREFLIES_TOKEN}",
                                                "Content-Type": "application/json"})
        response.raise_for_status()
        response = response.json()

    return response['data']['transcript']


def parse_conversation(data: dict) -> TranscriptionModel:
    date_string = data.get("dateString", "")
    sentences = data.get("sentences", [])

    users_set = set()
    transcription = []

    prev_speaker = None
    prev_text = ""

    for sentence in sentences:
        speaker = sentence.get("speaker_name") or "Speaker"
        text = sentence.get("text", "").strip()

        if not text:
            continue

        users_set.add(speaker)

        if speaker == prev_speaker:
            prev_text += " " + text
        else:
            if prev_speaker is not None:
                transcription.append({prev_speaker: prev_text})
            prev_speaker = speaker
            prev_text = text

    if prev_speaker is not None:
        transcription.append({prev_speaker: prev_text})

    users = sorted(users_set)

    return TranscriptionModel(
        dateString=date_string,
        users=users,
        transcription=transcription
    )


async def delete_call_transcription(transcription_id: str):
    mutation = '''
        mutation DeleteTranscript($transcriptId: String!) {
          deleteTranscript(id: $transcriptId) {
            id
            title
          }
        }
    '''
    data = {
        'query': mutation,
        'variables': {'transcriptId': transcription_id}
    }

    headers = {
        "Authorization": f"Bearer {settings.FIREFLIES_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        await client.post("https://api.fireflies.ai/graphql", json=data, headers=headers)


async def post_call_transcripton(transcription: TranscriptionModel):
    dt = datetime.fromisoformat(transcription.dateString.replace("Z", "+00:00"))

    date = dt.strftime("%d.%m.%Y")
    time = dt.strftime("%H:%M")
    members = ", ".join(transcription.users) if transcription.users else "None"

    template = f"""📞 New Call Report Is Ready!

👥 Members:
{members} 

📆 Date: {date}  
🕐 Time: {time}

📝 Summary:  
{transcription.summary}

🆔 ID: {transcription.id}"""

    await post_message("C092VC45THP", template)



