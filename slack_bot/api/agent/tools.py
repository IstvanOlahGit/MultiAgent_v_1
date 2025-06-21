import asyncio
from datetime import datetime
from typing import List, Literal

from langchain_community.tools import tool

from slack_bot.api.agent.utils import normalize_deadline_field, send_verification_email
from slack_bot.api.google.utils import find_doc_by_name, list_doc_names_range
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


@tool
async def get_document_names_tool(start: int = 1, end: int = 10, return_count_only: bool = False) -> int | List[str] | None:
    """Retrieve document names within a specific index range, or return the total number of available documents.

    Args:
        start (int): The starting index (inclusive) of the documents to retrieve. Must be >= 1.
        end (int): The ending index (exclusive) of the documents to retrieve.
        return_count_only (bool): If True, returns the total number of documents instead of their names.

    Returns:
        int | list[str] | None: Total number of documents if `return_count_only` is True,
                                otherwise a list of document names in the specified range,
                                or None if an error occurs.
    """
    try:
        docs = list_doc_names_range(start=start, end=end, return_count_only=return_count_only)
        return docs
    except Exception as e:
        print(f"[get_document_names_tool] Error: {e}")
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
async def query_mongo_tool(query: dict | list[dict], type_query: Literal["read", "insert", "update", "delete", "delete_many"]):
    """
    Perform an operation on the MongoDB 'tasks' collection.

    Args:
        query (dict | list[dict]):
            - For "read": a list of MongoDB aggregation pipeline stages (list of dicts).
            - For "insert": a single task document (dict) with keys:
                - task_description: str
                - employee: str
                - employee_id: str
                - deadline: datetime (can be ISO string or datetime object)
            - For "update": a dict with keys:
                - filter: dict — MongoDB filter to locate the task
                - update: dict — update operations (e.g., {"$set": {...}})
                  - If updating `deadline`, its value must be a Python datetime object, not a dict or string.
            - For "delete": a MongoDB filter (dict) identifying the task to delete
            - For "delete_many": a MongoDB filter (dict) to match multiple tasks to delete

        type_query (Literal): Type of the operation — one of "read", "insert", "update", "delete", "delete_many".

    Returns:
        Any: Result of the query or a confirmation message.
    """
    try:
        normalize_deadline_field(query)

        if type_query == "delete":
            await settings.DB_CLIENT.tasks.delete_one(query)
            return "Task deleted"
        elif type_query == "delete_many":
            result = await settings.DB_CLIENT.tasks.delete_many(query)
            return f"{result.deleted_count} task(s) deleted"
        elif type_query == "insert":
            await settings.DB_CLIENT.tasks.insert_one(query)
            return "Task inserted"
        elif type_query == "update":
            await settings.DB_CLIENT.tasks.update_one(query["filter"], query["update"])
            return "Task updated"
        elif type_query == "read":
            cursor = settings.DB_CLIENT.tasks.aggregate(query)
            results = await cursor.to_list(length=50)
            if not results:
                return "This employee has no tasks"
            return results
    except Exception as e:
        print(f"[query_mongo_tool] Error: {e}")
        return None


@tool
async def send_email_tool(emails: List[str], content: List[str]) -> None:
    """Send plain text emails to multiple employee email addresses.

        Args:
            emails: List[str] - A list of recipient employee email addresses.
            content: List[str] - A list of plain text contents for each email.
        Returns:
            None
        """
    try:
        if len(emails) != len(content):
            print("The number of emails must match the number of content entries.")

        await asyncio.gather(*[
            send_verification_email(email, message)
            for email, message in zip(emails, content)
        ])
    except Exception as e:
        print(f"[send_email_tool] Error: {e}")

