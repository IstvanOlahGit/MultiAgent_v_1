import asyncio
from datetime import datetime

from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

from slack_bot.api.agent.db_requests import save_messages
from slack_bot.api.agent.prompt import agent_prompts
from slack_bot.api.agent.tools import (
    get_document_tool,
    get_slack_users_tool,
    get_slack_user_tool,
    query_mongo_tool,
    get_document_names_tool,
    send_email_tool,
    query_mongo_transcription_tool
)
from slack_bot.core.config import settings


class SlackAgent:
    def __init__(self, channel_id: str, last_3_msg: list, message_history: MongoDBChatMessageHistory):
        self.channel_id = channel_id
        self.message_history = message_history
        self.flat_msgs = [msg for m in last_3_msg for msg in (m if isinstance(m, list) else [m])]
        self.now_str = datetime.now().isoformat()

        mongo_tools = [query_mongo_tool, get_slack_users_tool, get_slack_user_tool]
        mongo_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=agent_prompts.mongo_agent_prompt.system_prompt.format(
                    today=self.now_str,
                    channel_id=self.channel_id
                )
            ),
            MessagesPlaceholder(variable_name="messages")
        ])

        mongo_agent_executor = create_react_agent(
            model=settings.LLM_MINI.bind_tools(mongo_tools),
            prompt=mongo_prompt,
            tools=mongo_tools,
            name='MongoDBAgent'
        )

        docs_tools = [get_document_tool, get_document_names_tool]
        docs_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=agent_prompts.docs_agent_prompt.system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        docs_agent_executor = create_react_agent(
            model=settings.LLM_MINI.bind_tools(docs_tools),
            prompt=docs_prompt,
            tools=docs_tools,
            name='DocsAgent'
        )

        email_tools = [send_email_tool]
        email_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=agent_prompts.email_agent_prompt.system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        email_agent_executor = create_react_agent(
            model=settings.LLM_MINI.bind_tools(email_tools),
            prompt=email_prompt,
            tools=email_tools,
            name='EmailAgent'
        )

        transcription_tools = [query_mongo_transcription_tool]
        transcription_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=agent_prompts.mongo_transcription_agent_prompt.system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        transcription_agent_executor = create_react_agent(
            model=settings.LLM_MINI.bind_tools(email_tools),
            prompt=transcription_prompt,
            tools=transcription_tools,
            name='MongoDBTranscriptionAgent'
        )

        supervisor_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=agent_prompts.supervisor_prompt.system_prompt),
            *self.flat_msgs,
            MessagesPlaceholder(variable_name="messages")
        ])
        self.supervisor_workflow = create_supervisor(
            prompt=supervisor_prompt,
            model=settings.LLM_MINI,
            agents=[
                mongo_agent_executor,
                docs_agent_executor,
                email_agent_executor,
                transcription_agent_executor
            ],
            supervisor_name='supervisor'
        ).compile()


    async def run(self, content: str) -> str:
        result = await self.supervisor_workflow.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        })
        final_text = result["messages"][-1].content[0]["text"]
        asyncio.create_task(save_messages(content, final_text, self.message_history))
        return final_text