import unittest
import json
import os
import shutil
from app import app
from agents.analytics import AnalyticsAgent

class TestAdminDashboard(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clean up data before test
        if os.path.exists('data'):
            shutil.rmtree('data')
        os.makedirs('data')
        
        # Create some dummy data
        import pandas as pd
        df = pd.DataFrame({
            "Expectation": ["Learn"],
            "Domain": ["Finance"],
            "Project_Idea": ["Trading Bot"],
            "Programming_Confidence": ["High"],
            "AI_Experience": ["Advanced"],
            "Learning_Style": ["Hands-on"]
        })
        df.to_excel('data/responses.xlsx', index=False)

    def test_admin_routes(self):
        # 1. Test Admin Page Load
        rv = self.app.get('/admin')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Admin Dashboard', rv.data)

    def test_analytics_query(self):
        # 1. Trigger Analysis first
        self.app.post('/api/analyze')
        
        # 2. Test Query
        questions = [
            ("How many participants?", "1 participants"),
            ("How many advanced?", "1 advanced"),
            ("What domains?", "Finance"),
            ("What interests?", "Other") # Trading bot -> Other
        ]
        
        for q, expected in questions:
            rv = self.app.post('/api/admin/chat', json={'question': q})
            data = json.loads(rv.data)
            self.assertIn("answer", data)
            print(f"Q: {q} -> A: {data['answer']}")
            self.assertIn(expected, data['answer'])

if __name__ == '__main__':
    unittest.main()
