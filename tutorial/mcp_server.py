"""
FastMCP Testing Demo Server

A simple MCP server demonstrating tools, resources, and prompts
with comprehensive test coverage.
"""

import logging
import sys
import random
from typing import List
from fastmcp import FastMCP

# Configure logging to stderr to avoid interfering with stdout transport
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_server")

# Create server
mcp = FastMCP("Testing Demo")


# Tools
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    logger.info(f"Adding {a} + {b}")
    try:
        return a + b
    except Exception as e:
        logger.error(f"Error adding numbers: {e}")
        raise


@mcp.tool
def greet(name: str, greeting: str = "Hello") -> str:
    """Greet someone with a customizable greeting"""
    logger.info(f"Greeting {name} with '{greeting}'")
    return f"{greeting}, {name}!"


@mcp.tool
async def async_multiply(x: float, y: float) -> float:
    """Multiply two numbers (async example)"""
    logger.info(f"Multiplying {x} * {y}")
    return x * y


@mcp.tool
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate BMI and return category"""
    logger.info(f"Calculating BMI for weight={weight_kg}kg, height={height_m}m")
    if height_m <= 0:
        raise ValueError("Height must be positive")
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
        
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
        
    return f"BMI: {bmi:.1f} ({category})"


@mcp.tool
def get_random_joke() -> str:
    """Return a random programming joke"""
    logger.info("Fetching a random joke")
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
        "I would tell you a UDP joke, but you might not get it.",
        "Why did the programmer quit his job? He didn't get arrays.",
    ]
    return random.choice(jokes)


# Resources
@mcp.resource("demo://info")
def server_info() -> str:
    """Get server information"""
    logger.info("Accessing server info resource")
    return "This is the FastMCP Testing Demo server v2.0"


@mcp.resource("demo://greeting/{name}")
def greeting_resource(name: str) -> str:
    """Get a personalized greeting resource"""
    logger.info(f"Accessing greeting resource for {name}")
    return f"Welcome to FastMCP, {name}!"


# Prompts
@mcp.prompt("hello")
def hello_prompt(name: str = "World") -> str:
    """Generate a hello world prompt"""
    return f"Say hello to {name} in a friendly way."


@mcp.prompt("explain")
def explain_prompt(topic: str, detail_level: str = "medium") -> str:
    """Generate a prompt to explain a topic"""
    if detail_level == "simple":
        return f"Explain {topic} in simple terms for beginners."
    elif detail_level == "detailed":
        return f"Provide a detailed, technical explanation of {topic}."
    else:
        return f"Explain {topic} with moderate technical detail."

if __name__ == "__main__":
    mcp.run()