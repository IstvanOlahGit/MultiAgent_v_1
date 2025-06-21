import httpx

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
                                     headers=settings.get_header(settings.FIREFLIES_TOKEN))
        response.raise_for_status()
        response = response.json()

    return response['data']['transcript']
