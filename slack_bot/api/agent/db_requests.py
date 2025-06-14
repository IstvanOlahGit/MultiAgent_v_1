from typing import List, Union

from langchain_core.messages import HumanMessage, AIMessage
from langchain_mongodb import MongoDBChatMessageHistory


from slack_bot.core.config import settings


async def get_last_3_messages(channel_id: str) -> List[Union[AIMessage, HumanMessage]]:
    collection = settings.MONGO_CLIENT["slack"]["messages"]

    human_cursor = collection.find(
        {"session_id": channel_id, "type": "human"}
    ).sort("_id", -1).limit(3)

    ai_cursor = collection.find(
        {"session_id": channel_id, "type": "ai"}
    ).sort("_id", -1).limit(3)

    human_docs = list(human_cursor)
    ai_docs = list(ai_cursor)

    human_messages = [HumanMessage(content=doc["content"]) for doc in reversed(human_docs)]
    ai_messages = [AIMessage(content=doc["content"]) for doc in reversed(ai_docs)]

    mixed = []
    for i in range(max(len(human_messages), len(ai_messages))):
        if i < len(human_messages):
            mixed.append(human_messages[i])
        if i < len(ai_messages):
            mixed.append(ai_messages[i])

    return mixed


async def get_message_history(channel_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(
        session_id=channel_id,
        client=settings.MONGO_CLIENT,
        connection_string=None,
        session_id_key="sessionId",
        database_name="slack",
        collection_name="messages",
    )


async def save_messages(
        query: str, response: str, message_history: MongoDBChatMessageHistory
) -> None:
    await message_history.aadd_messages(
        [
            HumanMessage(content=query),
            AIMessage(
                content=response,
            ),
        ]
    )






