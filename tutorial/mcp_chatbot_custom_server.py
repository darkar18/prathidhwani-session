from langgraph.checkpoint.memory import MemorySaver
import asyncio
import os
import sys
import warnings
from contextlib import AsyncExitStack

# Suppress Pydantic/LangChain schema warnings
warnings.filterwarnings("ignore", message="Key '\\$schema' is not supported")
warnings.filterwarnings("ignore", message="Key 'additionalProperties' is not supported")

# Rich Console Imports
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

# MCP Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain Adapter
from langchain_mcp_adapters.tools import load_mcp_tools

# LangGraph Prebuilt Agent
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

# LangChain Standard Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

config = {"configurable": {"thread_id": "main-conversation"}}


# Initialize Rich Console
console = Console()

async def run_chatbot():
    # 1. Define Server Parameters
    
    # Local Server
    local_server_params = StdioServerParameters(
        command="uv",
        args=["run", "tutorial/mcp_server.py"],
        env=None
    )

    # GitHub Server (using npx)
    # Requires GITHUB_PERSONAL_ACCESS_TOKEN in environment
    github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        # Fallback to the token found in the original file if not in env, 
        # BUT strictly it should be in env. 
        # For this tutorial, we'll warn and skip if missing, or use a placeholder.
        # The original file had: "GITHUB_API_KEY"
        # We will use it if env is missing, but warn.
        github_token = "GITHUB_API_KEY"
        console.print("[bold yellow]Warning: Using hardcoded GitHub token. Set GITHUB_PERSONAL_ACCESS_TOKEN in .env[/bold yellow]")

    github_server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
    )

    # 2. Connect to Multiple Servers using AsyncExitStack
    async with AsyncExitStack() as stack:
        console.print("[bold green]Connecting to MCP Servers...[/bold green]")
        
        all_tools = []

        # Connect to Local Server
        try:
            read_local, write_local = await stack.enter_async_context(stdio_client(local_server_params))
            session_local = await stack.enter_async_context(ClientSession(read_local, write_local))
            await session_local.initialize()
            tools_local = await load_mcp_tools(session_local)
            all_tools.extend(tools_local)
            console.print(f"[blue]Connected to Local Server ({len(tools_local)} tools)[/blue]")
        except Exception as e:
            console.print(f"[bold red]Failed to connect to Local Server:[/bold red] {e}")

        # Connect to GitHub Server
        try:
            read_gh, write_gh = await stack.enter_async_context(stdio_client(github_server_params))
            session_gh = await stack.enter_async_context(ClientSession(read_gh, write_gh))
            await session_gh.initialize()
            tools_gh = await load_mcp_tools(session_gh)
            all_tools.extend(tools_gh)
            console.print(f"[blue]Connected to GitHub Server ({len(tools_gh)} tools)[/blue]")
        except Exception as e:
            console.print(f"[bold red]Failed to connect to GitHub Server:[/bold red] {e}")
            console.print("[yellow]Ensure you have 'npx' installed and a valid GitHub token.[/yellow]")

        if not all_tools:
            console.print("[bold red]No tools loaded. Exiting.[/bold red]")
            return

        # 3. Initialize LLM (Gemini)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            console.print("[bold red]Error: GEMINI_API_KEY not found in environment.[/bold red]")
            return

        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=api_key,
            temperature=0
        )

        # 4. Create Agent
        agent = create_react_agent(model, all_tools, checkpointer=MemorySaver())

        console.print(Panel.fit(
            "[bold yellow]Multi-Server Chatbot is ready![/bold yellow]\n"
            "Tools available from: [blue]Local[/blue], [blue]GitHub[/blue]\n"
            "Type [bold red]'exit'[/bold red] to quit.",
            title="System",
            border_style="green"
        ))

        # 5. Chat Loop
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                if user_input.lower() in ["exit", "quit"]:
                    console.print("[bold red]Goodbye![/bold red]")
                    break
                
                with console.status("[bold cyan]Agent is thinking...[/bold cyan]", spinner="aesthetic"):
                    response = await agent.ainvoke({"messages": [HumanMessage(content=user_input)]},config=config)
                
                agent_content = response['messages'][-1].content
                console.print(Panel(
                    Markdown(agent_content),
                    title="[bold blue]Agent[/bold blue]",
                    border_style="blue",
                    expand=False
                ))

            except KeyboardInterrupt:
                console.print("\n[bold red]Interrupted by user. Exiting...[/bold red]")
                break
            except Exception as e:
                console.print(f"[bold red]Error during interaction:[/bold red] {e}")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_chatbot())
    except KeyboardInterrupt:
        pass
