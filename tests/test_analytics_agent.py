import unittest
import os
import pandas as pd
from agents.analytics import AnalyticsAgent
from dotenv import load_dotenv

load_dotenv()

class TestAnalyticsAgent(unittest.TestCase):
    def setUp(self):
        # Create dummy data
        self.data_file = 'data/test_responses.xlsx'
        os.makedirs('data', exist_ok=True)
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Experience': ['Beginner', 'Intermediate', 'Advanced'],
            'Interest': ['Web', 'AI', 'Web'],
            'Confidence': ['High', 'Medium', 'Low']
        })
        df.to_excel(self.data_file, index=False)
        
        self.agent = AnalyticsAgent(data_file=self.data_file)

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_agent_query(self):
        if not os.getenv("GEMINI_API_KEY"):
            print("Skipping test: GEMINI_API_KEY not found")
            return

        response = self.agent.query("How many participants are there?")
        print(f"Agent Response: {response}")
        self.assertIn("3", response)

    def test_cross_tabulate(self):
        if not os.getenv("GEMINI_API_KEY"):
            return
        # Direct tool test (bypassing agent for unit testing helper)
        from agents.analytics import cross_tabulate
        result = cross_tabulate(self.data_file, 'Experience', 'Confidence')
        self.assertIn("Beginner", result)

    def test_memory(self):
        if not os.getenv("GEMINI_API_KEY"):
            return
        # 1. Ask a question
        q1 = "My name is Alesk."
        self.agent.query(q1, thread_id="test_thread")
        
        # 2. Ask follow-up that requires memory
        q2 = "What is my name?"
        response = self.agent.query(q2, thread_id="test_thread")
        print(f"Memory Response: {response}")
        self.assertIn("Alesk", response)

    def test_uuid_generation(self):
        # Test that WarmUpBot adds UUID
        from agents.chatbot import WarmUpBot
        bot = WarmUpBot()
        # Mock saving a response
        user_data = {"name": "Test User", "email": "test@example.com"}
        responses = ["Expectation", "Domain", "Project", "High", "Advanced", "Visual"]
        
        # Use a temporary file for this test
        bot.data_file = "test_data_uuid.xlsx"
        if os.path.exists(bot.data_file):
            os.remove(bot.data_file)
            
        bot.save_response(responses, user_data)
        
        df = pd.read_excel(bot.data_file)
        self.assertIn("UUID", df.columns)
        self.assertTrue(len(df['UUID'][0]) > 10)
        
        # Cleanup
        if os.path.exists(bot.data_file):
            os.remove(bot.data_file)

    def test_generate_report(self):
        if not os.getenv("GEMINI_API_KEY"):
            return
        
        # Test the generate_report tool via query
        response = self.agent.query("Generate a report for me.", thread_id="test_report")
        print(f"Report Response: {response}")
        
        # Check for link
        self.assertIn("static/audience_report.txt", response)
        
        # Check if file exists
        self.assertTrue(os.path.exists("static/audience_report.txt"))

if __name__ == '__main__':
    unittest.main()
