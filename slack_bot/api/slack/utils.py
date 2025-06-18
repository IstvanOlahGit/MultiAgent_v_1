from typing import List

import httpx
from slack import WebClient
from slack.errors import SlackApiError

from slack_bot.api.user.model import SlackUserModel
from slack_bot.core.config import settings


slack_client = WebClient(token=settings.SLACK_BOT_TOKEN)


async def post_message(channel, text):
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": text}
        )


def get_user_info(user_id: str) -> SlackUserModel | None:
    try:
        response = slack_client.users_info(user=user_id)
        user_info = response["user"]
        if not user_info['is_bot']:
            print(user_info)
            user_profile_info = user_info['profile']
            name = user_profile_info["first_name"] + " " + user_profile_info["last_name"]
            email = user_profile_info["email"]
            user = SlackUserModel(
                position=user_profile_info["title"],
                name=name,
                email=email,
                employee_id=user_id
            )
            return user
        return None
    except SlackApiError as e:
        print(f"Error while retrieving user info: {e.response['error']}")


def get_channel_users(channel_id: str) -> List[str]:
    try:
        members = []
        cursor = None
        while True:
            response = slack_client.conversations_members(channel=channel_id, cursor=cursor)
            members.extend(response['members'])
            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
        return members
    except SlackApiError as e:
        print(f"Error while retrieving channel participants: {e.response['error']}")


