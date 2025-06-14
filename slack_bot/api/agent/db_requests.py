import json
from typing import List, Union

from langchain_core.messages import HumanMessage, AIMessage
from langchain_mongodb import MongoDBChatMessageHistory


from slack_bot.core.config import settings


def get_last_3_messages(channel_id: str) -> List:
    collection = settings.MONGO_CLIENT["slack"]["messages"]

    cursor = collection.find(
        {"sessionId": channel_id}
    ).sort("_id", -1).limit(100)

    human_messages = []
    ai_messages = []

    for doc in cursor:
        raw = doc.get("History")
        if not raw:
            continue

        try:
            parsed = json.loads(raw)
            msg_type = parsed.get("type")
            content = parsed.get("data", {}).get("content", "")

            if msg_type == "human" and len(human_messages) < 3:
                human_messages.append(HumanMessage(content=content))
            elif msg_type == "ai" and len(ai_messages) < 3:
                ai_messages.append(AIMessage(content=content))

            if len(human_messages) == 3 and len(ai_messages) == 3:
                break

        except (json.JSONDecodeError, KeyError):
            continue

    human_messages.reverse()
    ai_messages.reverse()

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


if __name__ == "__main__":
    print(get_last_3_messages('C090VM7R2AU'))



