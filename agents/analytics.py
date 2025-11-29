import pandas as pd
import os
import json
import operator
from typing import TypedDict, Annotated, List, Union
from functools import partial

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool, StructuredTool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()

# --- Tools ---
def get_dataset_info(data_file: str) -> str:
    """Returns basic information about the dataset (columns, shape, sample)."""
    if not os.path.exists(data_file):
        return "Data file does not exist."
    try:
        df = pd.read_excel(data_file)
        if df.empty:
            return "Dataset is empty."
        info = f"Columns: {list(df.columns)}\nShape: {df.shape}\nSample:\n{df.head(2).to_string()}"
        return info
    except Exception as e:
        return f"Error reading data: {e}"

def count_values(data_file: str, column: str) -> str:
    """Counts unique values in a specific column."""
    try:
        df = pd.read_excel(data_file)
        if column not in df.columns:
            return f"Column '{column}' not found. Available: {list(df.columns)}"
        counts = df[column].value_counts().to_dict()
        return json.dumps(counts, indent=2)
    except Exception as e:
        return f"Error: {e}"

def filter_and_count(data_file: str, filter_col: str, filter_val: str, count_col: str) -> str:
    """Filters data by a column value (substring match) and counts values in another column."""
    try:
        df = pd.read_excel(data_file)
        # Case insensitive string match
        filtered = df[df[filter_col].astype(str).str.contains(filter_val, case=False, na=False)]
        if filtered.empty:
            return "No matching records found."
        counts = filtered[count_col].value_counts().to_dict()
        return json.dumps(counts, indent=2)
    except Exception as e:
        return f"Error: {e}"

def cross_tabulate(data_file: str, row_col: str, col_col: str) -> str:
    """Creates a cross-tabulation (contingency table) between two columns."""
    try:
        df = pd.read_excel(data_file)
        if row_col not in df.columns or col_col not in df.columns:
            return f"Columns not found. Available: {list(df.columns)}"
        ct = pd.crosstab(df[row_col], df[col_col])
        return ct.to_json()
    except Exception as e:
        return f"Error: {e}"

def get_raw_data(data_file: str, limit: int = 5) -> str:
    """Returns a sample of raw rows for qualitative analysis."""
    try:
        df = pd.read_excel(data_file)
        return df.head(limit).to_json(orient='records')
    except Exception as e:
        return f"Error: {e}"



# --- Agent ---
class AnalyticsAgent:
    def __init__(self, data_file='data/responses.xlsx'):
        self.data_file = data_file
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.app = None
        
        if self.api_key:
            self._setup_graph()

    def _setup_graph(self):
        # 1. Bind data_file to tools
        # 1. Bind data_file to tools
        def _get_dataset_info():
            """Returns basic information about the dataset (columns, shape, sample)."""
            return get_dataset_info(self.data_file)

        def _count_values(column: str):
            """Counts unique values in a specific column."""
            return count_values(self.data_file, column)

        def _filter_and_count(filter_col: str, filter_val: str, count_col: str):
            """Filters data by a column value (substring match) and counts values in another column."""
            return filter_and_count(self.data_file, filter_col, filter_val, count_col)

        def _cross_tabulate(row_col: str, col_col: str):
            """Creates a cross-tabulation (contingency table) between two columns."""
            return cross_tabulate(self.data_file, row_col, col_col)

        def _get_raw_data(limit: int = 5):
            """Returns a sample of raw rows for qualitative analysis."""
            return get_raw_data(self.data_file, limit)

        def _generate_report():
            """Generates a text report of the analysis and returns a download link."""
            from agents.writer import WriterAgent
            # Perform analysis
            data = self.analyze()
            # Generate report
            writer = WriterAgent()
            writer.write_report(data)
            return "Report generated! [Download Report](/static/audience_report.txt)"

        tools = [
            StructuredTool.from_function(
                _get_dataset_info,
                name="get_dataset_info",
                description="Get info about dataset columns and shape."
                
            ),
            StructuredTool.from_function(
                _count_values,
                name="count_values",
                description="Count unique values in a column."
            ),
            StructuredTool.from_function(
                _filter_and_count,
                name="filter_and_count",
                description="Filter data by one column and count values in another."
            ),
            StructuredTool.from_function(
                _cross_tabulate,
                name="cross_tabulate",
                description="Create a contingency table between two columns."
            ),
            StructuredTool.from_function(
                _get_raw_data,
                name="get_raw_data",
                description="Get raw data rows for qualitative analysis."
            ),
            StructuredTool.from_function(
                _generate_report,
                name="generate_report",
                description="Generate a comprehensive text report and get a download link."
            )
        ]

        # 2. Setup LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=self.api_key)
        
        system_prompt = """You are an expert Data Analyst for an AI Workshop. 
        Your goal is to provide deep, actionable insights, not just numbers.
        
        When asked to analyze:
        1. ALWAYS start by checking the dataset info.
        2. Look for patterns using cross-tabulation (e.g., Experience vs Confidence, Domain vs Project Idea).
        3. Read raw project ideas to identify themes.
        4. Be proactive: if you see a trend, explain WHY it might be happening.
        5. Use a professional but engaging tone.
        """

        # 3. Create Agent
        self.checkpointer = MemorySaver()
        self.app = create_react_agent(llm, tools=tools, checkpointer=self.checkpointer)

    def analyze(self):
        """
        Performs a full analysis to generate the summary JSON expected by the report writer.
        """
        if not self.app:
            return {"error": "Gemini API Key missing."}

        system_prompt = """You are an expert Data Analyst for an AI Workshop. 
        Your goal is to provide deep, actionable insights, not just numbers.
        
        When asked to analyze:
        1. ALWAYS start by checking the dataset info.
        2. Look for patterns using cross-tabulation (e.g., Experience vs Confidence, Domain vs Project Idea).
        3. Read raw project ideas to identify themes.
        4. Be proactive: if you see a trend, explain WHY it might be happening.
        5. Use a professional but engaging tone.
        """

        prompt = """
        Analyze the dataset and return a JSON object with these keys:
        - total_participants (int)
        - experience_breakdown (dict)
        - confidence_breakdown (dict)
        - top_domains (dict)
        - interest_clusters (dict - group similar project ideas)

        Use the tools to get the data. Return ONLY the JSON.
        """
        
        try:
            inputs = {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]}
            result = self.app.invoke(inputs,config={"configurable": {"thread_id": "admin_session"}})
            last_msg = result["messages"][-1].content
            if isinstance(last_msg, list):
                last_msg = " ".join([block['text'] for block in last_msg if 'text' in block])
            
            # Clean up code blocks if present
            clean_json = last_msg.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Analysis failed: {e}")
            return {"error": str(e)}

    def query(self, question, thread_id="admin_session"):
        """
        Answers a specific user question using the graph.
        """
        if not self.app:
            return "I need a Gemini API Key to answer questions."

        try:
            config = {"configurable": {"thread_id": thread_id}}
            inputs = {"messages": [HumanMessage(content=question)]}
            result = self.app.invoke(inputs, config=config)
            content = result["messages"][-1].content
            if isinstance(content, list):
                return " ".join([block['text'] for block in content if 'text' in block])
            return content
        except Exception as e:
            return f"I encountered an error: {e}"
