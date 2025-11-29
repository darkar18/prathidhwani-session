import unittest
import json
import os
import shutil
from app import app

class TestAudienceSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clean up data before test
        if os.path.exists('data'):
            shutil.rmtree('data')
        os.makedirs('data')

    def test_full_flow(self):
        # 1. Simulate User Chat
        # User 1
        responses = [
            "I want to learn about agents", # Expectation
            "Healthcare", # Domain
            "A medical diagnosis agent", # Project Idea
            "Medium", # Programming Confidence
            "Beginner", # AI Experience
            "Hands-on" # Learning Style
        ]
        
        # Initial greeting (no input needed really, but let's say we send "Hi")
        self.app.post('/api/chat', json={'message': "Hi"})
        
        for ans in responses:
            rv = self.app.post('/api/chat', json={'message': ans})
            data = json.loads(rv.data)
            self.assertIn("response", data)
            print(f"Bot: {data['response']}")

        # 2. Verify Data Storage
        self.assertTrue(os.path.exists('data/responses.xlsx'))
        
        # 3. Trigger Analytics & Report
        rv = self.app.post('/api/analyze')
        data = json.loads(rv.data)
        
        self.assertIn("analytics", data)
        self.assertIn("report", data)
        
        print("Analytics:", data['analytics'])
        
        # 4. Verify Report File
        self.assertTrue(os.path.exists('data/audience_report.txt'))
        with open('data/audience_report.txt', 'r') as f:
            content = f.read()
            self.assertIn("TOTAL PARTICIPANTS: 1", content)
            self.assertIn("Healthcare", content)

if __name__ == '__main__':
    unittest.main()
