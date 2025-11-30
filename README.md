# 🤖 Building AI Agents with MCP & Flask

Welcome to the **Prathidhwani Session** workshop! This repository contains the material for building intelligent AI agents using the **Model Context Protocol (MCP)** and **Flask**.

By the end of this tutorial, you will have built a web-based chatbot that can:
1.  Understand user intent.
2.  Remember conversation history.
3.  Use tools (like checking the weather or analyzing data).
4.  Generate reports based on user interactions.

---

## 🚀 Getting Started

### Prerequisites
-   **Python 3.14+** (Recommended)
-   **Google Gemini API Key** (or another LLM provider supported by LangChain)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd prathidhwani-session-main
    ```

2.  **Install dependencies**:
    You can use `uv` (recommended) or `pip`.

    **Using uv (Recommended)**:
    ```bash
    uv sync
    ```

    **Using pip**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory and add your API keys:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

---

## 📚 Tutorial Modules

The `tutorial/` directory contains step-by-step scripts to help you understand the core concepts.

### Module 1: The End Goal 🏁
Before we build, let's see what we are aiming for. Run the main Flask application:

```bash
python app.py
```
-   Open your browser at `http://localhost:5000`.
-   Interact with the "WarmUpBot".
-   Check the Admin Dashboard at `http://localhost:5000/admin`.

### Module 2: MCP Basics 🔌
Understand how the **Model Context Protocol** works.
-   **Server**: `tutorial/mcp_server.py` - A simple MCP server that provides tools.
-   **Client**: `tutorial/mcp_client.py` - A client that connects to the server and uses its tools.

### Module 3: Building the Chatbot 🤖

#### Step 1: Basic Bot
**File**: `tutorial/mcp_chatbot.py`
A simple chatbot that connects to an LLM and responds to user queries.

#### Step 2: Adding Memory 🧠
**File**: `tutorial/mcp_chatbot_memory.py`
Enhance the bot to remember previous interactions in the conversation.

#### Step 3: Tool Use 🛠️
**File**: `tutorial/mcp_chatbot_color.py`
Give the bot the ability to call external functions (tools), like changing the color of the terminal output.

#### Step 4: Custom Servers 🖥️
**File**: `tutorial/mcp_chatbot_custom_server.py`
Learn how to create a custom MCP server to expose your own data or API to the chatbot.

---

## 🏗️ Project Structure

-   **`app.py`**: The main Flask application entry point.
-   **`agents/`**: Contains the logic for different agents.
    -   `chatbot.py`: The main conversational agent.
    -   `analytics.py`: Agent for analyzing session data.
    -   `writer.py`: Agent for generating reports.
-   **`data/`**: Stores session data (Excel files) and reports.
-   **`static/`**: HTML, CSS, and JavaScript files for the frontend.
-   **`tutorial/`**: Step-by-step learning scripts.

---

## 🤝 Contributing
Feel free to fork this repository and submit pull requests if you have any improvements or bug fixes.

Happy Coding! 🚀
