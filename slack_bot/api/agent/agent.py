import asyncio
from datetime import datetime

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from slack_bot.api.agent.db_requests import save_messages
from slack_bot.api.agent.prompt import global_agent_prompts
from slack_bot.api.agent.tools import (get_document_tool,
                                       get_slack_users_tool,
                                       get_slack_user_tool,
                                       query_mongo_tool,
                                       get_document_names_tool, send_email_tool)
from slack_bot.core.config import settings



class SlackAgent:
    def __init__(self, channel_id: str, last_3_msg: list, message_history: MongoDBChatMessageHistory):
        self.tools = [
            get_document_tool,
            get_slack_users_tool,
            get_slack_user_tool,
            query_mongo_tool,
            get_document_names_tool,
            send_email_tool
        ]
        self.LLM = settings.LLM_MINI.bind_tools(self.tools)
        self.message_history = message_history

        flat_msgs = []
        for i, msg in enumerate(last_3_msg):
            if isinstance(msg, list):
                flat_msgs.extend(msg)
            else:
                flat_msgs.append(msg)

        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=global_agent_prompts.system_prompt.format(
                    today=datetime.now().isoformat(),
                    channel_id=channel_id
                )
            ),
            *flat_msgs,
            ("human", "{content}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(
            llm=self.LLM,
            prompt=self.prompt,
            tools=self.tools,
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
        )

    async def run(self, content: str) -> str:
        response = await self.agent_executor.ainvoke({"content": content})
        asyncio.create_task(save_messages(content, response["output"][-1]["text"], self.message_history))
        return response["output"][-1]["text"]