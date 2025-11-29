import operator
from typing import TypedDict, Annotated, List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
load_dotenv()


# Define the state for the graph 
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# Define a simple tool
@tool
def search_tool(query: str) -> str:
    """Searches for information on the web."""
    # In a real application, this would call a search API.
    # For this example, we'll return a static response.
    if "weather" in query.lower():
        return "The weather in San Francisco is sunny with a temperature of 70F."
    return f"Information about '{query}' is not available in this mock search."


# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Bind the tool to the LLM
tool_llm = llm.bind_tools([search_tool])


# Define the agent node
def agent_node(state: AgentState) -> dict:
    """
    The agent node that decides whether to call a tool or respond directly.
    """
    messages = state["messages"]
    response = tool_llm.invoke(messages)
    return {"messages": [response]}


# Define the tool node
def tool_node(state: AgentState) -> dict:
    """
    The tool node that executes the tool call.
    """
    messages = state["messages"]
    last_message = messages[-1]
    tool_calls = last_message.tool_calls
    tool_outputs = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        if tool_name == "search_tool":
            output = search_tool.invoke(tool_args)
            tool_outputs.append(ToolMessage(content=str(output), tool_call_id=tool_call["id"]))
    return {"messages": tool_outputs}


# Define the conditional edge logic (router)
def should_continue(state: AgentState) -> str:
    """
    Determines whether the agent should continue by calling a tool or finish.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "call_tool"
    return "end"


# Build the LangGraph workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tool", tool_node)

# Set the entry point
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",  # From the agent node
    should_continue,  # Use the router function to decide next step
    {
        "call_tool": "tool",  # If tool should be called, go to the tool node
        "end": END,  # If not, end the conversation
    },
)

# Add a normal edge from the tool node back to the agent node
workflow.add_edge("tool", "agent")

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    # Example usage
    inputs = {"messages": [HumanMessage(content="What's the weather in San Francisco?")]}
    for s in app.stream(inputs):
        print(s)
        print("---")

    print("\n--- New Conversation ---")
    inputs = {"messages": [HumanMessage(content="Hello, how are you?")]}
    for s in app.stream(inputs):
        print(s)
        print("---")
