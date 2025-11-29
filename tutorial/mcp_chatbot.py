import asyncio
import os
import sys

# MCP Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain Adapter
from langchain_mcp_adapters.tools import load_mcp_tools

# LangGraph Prebuilt Agent (Self-executing, no AgentExecutor needed)
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

# LangChain Standard Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

async def run_chatbot():
    # 1. Define Server Parameters for Local STDIO
    # This example assumes you are running a local server script.
    # Adjust 'command' and 'args' to match your specific MCP server.
    server_params = StdioServerParameters(
        command="uv",                 # Executable (e.g., 'uv', 'python', 'node')
        args=["run", "tutorial/mcp_server.py"],    # Arguments (e.g., script path)
        env=None                      # Environment variables if needed
    )

    print("Connecting to Local MCP Server via STDIO...")

    # 2. Connect using STDIO Transport
    # The client yields (read_stream, write_stream)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. Load Remote Tools
            # This fetches the tool definitions from the local server process
            langchain_tools = await load_mcp_tools(session)
            print(f"Successfully loaded {len(langchain_tools)} tools.")

            # 4. Initialize LLM (Gemini)
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print("Error: GEMINI_API_KEY not found in environment.")
                return

            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                google_api_key=api_key,
                temperature=0
            )

            # 5. Create Agent
            # The LangGraph create_react_agent returns a compiled graph that executes itself
            agent = create_react_agent(model, langchain_tools)

            print("Chatbot is ready! Type 'exit' to quit.")

            # 6. Chat Loop
            while True:
                try:
                    user_input = input("\nYou: ")
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    
                    # Run the agent
                    # LangGraph expects a list of messages
                    response = await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})
                    
                    # The response contains the full history; the last message is the AI's answer
                    print(f"Agent: {response['messages'][-1].content}")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error during interaction: {e}")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_chatbot())
    except KeyboardInterrupt:
        pass