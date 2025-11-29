import unittest
import json
import os
import shutil
import pandas as pd
from app import app

class TestUserPanel(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clean up data before test
        if os.path.exists('data'):
            shutil.rmtree('data')
        os.makedirs('data')

    def test_user_flow_with_validation(self):
        user_data = {"name": "Test User", "email": "test@example.com"}
        
        # 1. Start Session
        rv = self.app.post('/api/chat', json={
            'message': "START_SESSION", 
            'user_data': user_data
        })
        data = json.loads(rv.data)
        self.assertIn("Hi Test User!", data['response'])

        # 2. Answer Questions
        responses = [
            "I want to learn", # Expectation
            "Finance", # Domain -> Should trigger reaction
            "Trading Bot", # Project Idea
        ]
        
        for ans in responses:
            rv = self.app.post('/api/chat', json={'message': ans, 'user_data': user_data})
            data = json.loads(rv.data)
            if "Finance" in ans:
                self.assertIn("Finance is a great domain", data['response'])

        # 3. Test Validation (Confidence Question is index 3)
        # Send invalid answer
        rv = self.app.post('/api/chat', json={'message': "Not sure", 'user_data': user_data})
        data = json.loads(rv.data)
        self.assertIn("Please answer with Low, Medium, or High", data['response'])
        
        # Send valid answer
        rv = self.app.post('/api/chat', json={'message': "High", 'user_data': user_data})
        data = json.loads(rv.data)
        self.assertIn("Awesome", data['response']) # Reaction to "High"

        # 4. Test Gibberish (Next question is Experience)
        rv = self.app.post('/api/chat', json={'message': "a", 'user_data': user_data})
        data = json.loads(rv.data)
        self.assertIn("Could you elaborate", data['response'])
        
        # Send valid answer
        rv = self.app.post('/api/chat', json={'message': "Beginner", 'user_data': user_data})

        # Last question (Learning Style)
        rv = self.app.post('/api/chat', json={'message': "Hands-on", 'user_data': user_data})
        
        # 5. Verify Data Storage
        self.assertTrue(os.path.exists('data/responses.xlsx'))
        df = pd.read_excel('data/responses.xlsx')
        self.assertEqual(df.iloc[0]['Name'], "Test User")
        self.assertEqual(df.iloc[0]['Email'], "test@example.com")

if __name__ == '__main__':
    unittest.main()
