import asyncio
import os
import sys

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

# LangGraph Prebuilt Agent (Self-executing, no AgentExecutor needed)
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

# LangChain Standard Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Rich Console
console = Console()

async def run_chatbot():
    # 1. Define Server Parameters for Local STDIO
    # This example assumes you are running a local server script.
    # Adjust 'command' and 'args' to match your specific MCP server.
    server_params = StdioServerParameters(
        command="uv",                 # Executable (e.g., 'uv', 'python', 'node')
        args=["run", "tutorial/mcp_server.py"],    # Arguments (e.g., script path)
        env=None                      # Environment variables if needed
    )

    # 2. Connect using STDIO Transport
    # Note: stdio_client and ClientSession must remain open for the duration of the chat
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Use a spinner ONLY for the initialization phase
            with console.status("[bold green]Connecting to Local MCP Server...[/bold green]", spinner="dots"):
                await session.initialize()
                
                # 3. Load Remote Tools
                # This fetches the tool definitions from the local server process
                langchain_tools = await load_mcp_tools(session)
            
            # Spinner stops here automatically when exiting the 'with' block
            console.print(f"[bold blue]Successfully loaded {len(langchain_tools)} tools.[/bold blue] ✓")

            # 4. Initialize LLM (Gemini)
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                console.print("[bold red]Error: GEMINI_API_KEY not found in environment.[/bold red]")
                return

            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                google_api_key=api_key,
                temperature=0
            )

            # 5. Create Agent
            # The LangGraph create_react_agent returns a compiled graph that executes itself
            agent = create_react_agent(model, langchain_tools)

            console.print(Panel.fit(
                "[bold yellow]Chatbot is ready![/bold yellow]\nType [bold red]'exit'[/bold red] to quit.",
                title="System",
                border_style="green"
            ))

            # 6. Chat Loop
            while True:
                try:
                    # Use Rich Prompt
                    user_input = Prompt.ask("\n[bold green]You[/bold green]")
                    
                    if user_input.lower() in ["exit", "quit"]:
                        console.print("[bold red]Goodbye![/bold red]")
                        break
                    
                    # Show a spinner while the agent thinks
                    with console.status("[bold cyan]Agent is thinking...[/bold cyan]", spinner="aesthetic"):
                        response = await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})
                    
                    # Render response as Markdown inside a Panel
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