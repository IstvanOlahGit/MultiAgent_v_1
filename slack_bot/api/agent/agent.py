import asyncio
from datetime import datetime

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage


from slack_bot.api.agent.prompt import global_agent_prompts
from slack_bot.core.config import settings



class SlackAgent:
    def __init__(self):
        self.tools = [
        ]
        self.LLM = settings.LLM_MINI.bind_tools(self.tools)

        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=global_agent_prompts.system_prompt.format(
                    today=datetime.now().isoformat(),
                )
            ),
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
        return response["output"][-1]["text"]