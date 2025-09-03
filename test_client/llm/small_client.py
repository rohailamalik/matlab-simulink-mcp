from fastmcp import Client
import asyncio

async def main():
    async with Client(r"C:\Data\Research\Doctoral\src\matlab-simulink-mcp\src\matlab_simulink_mcp\main.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")


    
asyncio.run(main())