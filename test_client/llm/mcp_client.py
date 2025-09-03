from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from tests.llm.model import model
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
import pprint

server_params = StdioServerParameters(
    command="python",
    args=[r"c:/Data/Research/Doctoral/src/matlab-simulink-mcp/math_server.py"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            agent = create_react_agent(model=model, tools=tools)
            agent_response = await agent.ainvoke({
                "messages": [
                    {"role": "user", "content": "what's (3 + 5) x 12?"}
                ]
            })
            return agent_response

resp = asyncio.run(main())
pprint.pprint(resp)
