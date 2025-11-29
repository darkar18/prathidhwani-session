import pandas as pd
import os
import uuid
from datetime import datetime

class WarmUpBot:
    def __init__(self):
        self.questions = [
            "What’s your expectation for today?",
            "What’s your background domain? (e.g., Finance, Healthcare, Tech)",
            "What kind of AI agent do you want to build?",
            "How comfortable are you with programming / Python? (Low/Medium/High)",
            "What’s your experience in AI? (Beginner/Intermediate/Advanced)",
            "Do you prefer hands-on or conceptual explanations?"
        ]
        self.sessions = {}
        self.data_file = 'data/responses.xlsx'

    def get_response(self, user_id, message, user_data=None):
        if user_id not in self.sessions:
            self.sessions[user_id] = {'step': 0, 'responses': [], 'user_data': user_data}
            # If message is START_SESSION, just return the first question
            if message == "START_SESSION":
                 return f"Hi {user_data.get('name', 'there')}! " + self.questions[0]
            return self.questions[0]

        session = self.sessions[user_id]
        step = session['step']

        # Validation & Reaction Logic
        current_question = self.questions[step]
        reaction = ""
        
        # Simple validation/reaction based on step
        if step == 3: # Programming Confidence
            valid_options = ["low", "medium", "high"]
            if not any(opt in message.lower() for opt in valid_options):
                return "Please answer with Low, Medium, or High so I can tailor the content."
        
        # Gibberish check (too short) - Only for Expectation (0) and Project Idea (2)
        if len(message.split()) < 2 and step not in [1, 3, 4, 5]: 
             return "Could you elaborate a bit more on that? I want to make sure I understand."

        # Reactions
        if "finance" in message.lower():
            reaction = "Finance is a great domain for AI agents! 📈 "
        elif "healthcare" in message.lower():
            reaction = "Healthcare AI is very impactful! 🏥 "
        elif "python" in message.lower() and "high" in message.lower():
            reaction = "Awesome, you'll breeze through the code! 🐍 "

        # Store the answer
        if step < len(self.questions):
            session['responses'].append(message)
            session['step'] += 1
        
        # Check if we have more questions
        if session['step'] < len(self.questions):
            next_q = self.questions[session['step']]
            return f"{reaction}{next_q}"
        else:
            # Finished
            self.save_response(session['responses'], session.get('user_data'))
            del self.sessions[user_id]
            return f"{reaction}Thanks! I've recorded your profile. Sit tight, the workshop is about to begin! 🚀"

    def save_response(self, responses, user_data):
        # Map responses to columns
        columns = [
            "Expectation", "Domain", "Project_Idea", 
            "Programming_Confidence", "AI_Experience", "Learning_Style"
        ]
        
        new_data = {col: [val] for col, val in zip(columns, responses)}
        new_data['Timestamp'] = [datetime.now()]
        
        if user_data:
            new_data['Name'] = [user_data.get('name')]
            new_data['Email'] = [user_data.get('email')]
        
        # Add Unique ID
        new_data['UUID'] = [str(uuid.uuid4())]
        
        df_new = pd.DataFrame(new_data)
        
        if os.path.exists(self.data_file):
            df_existing = pd.read_excel(self.data_file)
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_final = df_new
            
        df_final.to_excel(self.data_file, index=False)
