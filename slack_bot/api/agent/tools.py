import asyncio
from typing import List

from langchain_community.tools import tool

from slack_bot.api.google.utils import find_doc_by_name
from slack_bot.api.slack.utils import get_channel_users, get_user_info
from slack_bot.api.user.model import SlackUserModel
from slack_bot.core.config import settings


@tool
async def get_document_tool(document_title: str) -> str | None:
    """Retrieve a document link by its title.

    Args:
        document_title: str - The title of the document to retrieve.
    Returns:
        str | None - A URL link to the document if found, otherwise None.
    """
    try:
        document = find_doc_by_name(document_title)
        return document
    except Exception as e:
        print(f"[get_document_tool] Error: {e}")
        return None


async def process_profile(user_id, semaphore):
    async with semaphore:
        return await asyncio.to_thread(get_user_info, user_id)


@tool
async def get_slack_users_tool(channel_id: str) -> List[SlackUserModel] | None:
    """Fetch Slack user profiles from a given channel.

    Args:
        channel_id: str - The ID of the Slack channel to fetch users from.
    Returns:
        List[SlackUserModel] | None - A list of Slack user profiles in the channel, or None if failed.
    """
    try:
        user_ids = get_channel_users(channel_id)
        semaphore = asyncio.Semaphore(10)
        profiles = await asyncio.gather(
            *[process_profile(user_id, semaphore) for user_id in user_ids]
        )
        return [profile for profile in profiles if profile]
    except Exception as e:
        print(f"[get_slack_users_tool] Error: {e}")
        return None


@tool
async def get_slack_user_tool(user_id: str) -> SlackUserModel | None:
    """Retrieve a single Slack user profile by user ID.

    Args:
        user_id: str - The Slack user ID.
    Returns:
        SlackUserModel | None - The user's profile object if found, otherwise None.
    """
    try:
        user = get_user_info(user_id)
        return user
    except Exception as e:
        print(f"[get_slack_user_tool] Error: {e}")
        return None


@tool
async def query_mongo_tool(query: list[dict]):
    """Query the MongoDB 'tasks' collection using a MongoDB query.

    Args:
        query: list[dict] - Aggregated query for MongoDB.
    Returns:
        Any - Result of the query.
    """
    try:
        cursor = settings.DB_CLIENT.tasks.aggregate(query)
        results = await cursor.to_list(length=50)
        if not results:
            return None
        return results
    except Exception as e:
        print(f"[query_mongo_tool] Error: {e}")
        return None


