import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import json
from agents.analytics import AnalyticsAgent

class TestAnalyticsGemini(unittest.TestCase):
    def setUp(self):
        # Create a dummy dataframe
        self.df = pd.DataFrame({
            "Domain": ["Edu", "School", "Finance"],
            "Project_Idea": ["Chatbot", "GPT", "Trading"],
            "AI_Experience": ["Beginner", "Beginner", "Advanced"],
            "Programming_Confidence": ["Low", "Low", "High"]
        })

    @patch('agents.analytics.genai')
    @patch('agents.analytics.os.getenv')
    def test_analyze_with_gemini_success(self, mock_getenv, mock_genai):
        # Mock API Key presence
        mock_getenv.return_value = "FAKE_KEY"
        
        # Mock Gemini Response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "total_participants": 3,
            "experience_breakdown": {"Beginner": 2, "Advanced": 1},
            "confidence_breakdown": {"Low": 2, "High": 1},
            "top_domains": {"Education": 2, "Finance": 1},
            "interest_clusters": {"LLMs": 2, "Finance": 1}
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Initialize Agent
        agent = AnalyticsAgent()
        # Inject dummy data file path (won't be used by analyze_with_gemini directly but needed for init)
        agent.data_file = "dummy.xlsx"
        
        # Call the method directly
        result = agent.analyze_with_gemini(self.df)
        
        self.assertEqual(result['total_participants'], 3)
        self.assertEqual(result['top_domains']['Education'], 2)
        self.assertEqual(result['interest_clusters']['LLMs'], 2)

    def test_fallback_logic(self):
        # Ensure fallback works when no API key
        agent = AnalyticsAgent()
        agent.api_key = None
        
        # Mock analyze_rule_based to return "Rule Based"
        agent.analyze_rule_based = MagicMock(return_value="Rule Based")
        
        # Mock pd.read_excel to return our df
        with patch('pandas.read_excel', return_value=self.df):
            with patch('os.path.exists', return_value=True):
                result = agent.analyze()
                self.assertEqual(result, "Rule Based")

if __name__ == '__main__':
    unittest.main()
