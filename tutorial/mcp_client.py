import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Define server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["tutorial/mcp_server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            print("\n--- Available Tools ---")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call 'add' tool
            print("\n--- Calling 'add' tool ---")
            result_add = await session.call_tool("add", arguments={"a": 10, "b": 20})
            print(f"10 + 20 = {result_add.content[0].text}")

            # Call 'greet' tool
            print("\n--- Calling 'greet' tool ---")
            result_greet = await session.call_tool("greet", arguments={"name": "Alice"})
            print(f"Greeting: {result_greet.content[0].text}")

            # Call 'calculate_bmi' tool
            print("\n--- Calling 'calculate_bmi' tool ---")
            result_bmi = await session.call_tool("calculate_bmi", arguments={"weight_kg": 70, "height_m": 1.75})
            print(f"BMI Result: {result_bmi.content[0].text}")

            # Call 'get_random_joke' tool
            print("\n--- Calling 'get_random_joke' tool ---")
            result_joke = await session.call_tool("get_random_joke", arguments={})
            print(f"Joke: {result_joke.content[0].text}")

            # Read resource
            print("\n--- Reading 'demo://info' resource ---")
            resources = await session.read_resource("demo://info")
            print(f"Resource Content: {resources.contents[0].text}")

if __name__ == "__main__":
    asyncio.run(run())
