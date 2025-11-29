import random
import time
from agents.chatbot import WarmUpBot

# Test Data Pools
NAMES = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Kevin", "Laura", "Mike", "Nina", "Oscar", "Pam", "Quinn", "Rachel", "Steve", "Tina"]
DOMAINS = ["Finance", "Healthcare", "Education", "Retail", "Tech", "Marketing", "Logistics", "Entertainment", "Real Estate", "Automotive"]
PROJECTS = ["Trading Bot", "Diagnosis Helper", "Tutor Bot", "Shopper Assistant", "Code Generator", "Ad Optimizer", "Route Planner", "Game NPC", "Price Predictor", "Car OS"]
CONFIDENCE = ["Low", "Medium", "High"]
EXPERIENCE = ["Beginner", "Intermediate", "Advanced"]
STYLES = ["Hands-on", "Conceptual", "Mix"]

def generate_random_user(index):
    name = NAMES[index % len(NAMES)]
    return {
        "name": f"{name} {random.randint(1, 100)}",
        "email": f"{name.lower()}{random.randint(1, 100)}@example.com"
    }

def populate():
    print("🚀 Starting Data Population (20 Users)...")
    bot = WarmUpBot()
    
    # Check initial count
    initial_count = 0
    if os.path.exists(bot.data_file):
        try:
            df = pd.read_excel(bot.data_file)
            initial_count = len(df)
            print(f"Initial data count: {initial_count}")
        except:
            print("Could not read existing data file.")

    for i in range(20):
        try:
            user_data = generate_random_user(i)
            user_id = f"sim_user_{i}_{int(time.time())}" # Unique ID
            
            print(f"\n[{i+1}/20] Simulating {user_data['name']} ({user_id})...")
            
            # 1. Start Session
            resp = bot.get_response(user_id, "START_SESSION", user_data)
            print(f"  Bot: {resp[:50]}...")
            
            # 2. Answer Questions
            # Q1: Expectation
            resp = bot.get_response(user_id, "I want to learn about AI agents.", user_data)
            
            # Q2: Domain
            domain = random.choice(DOMAINS)
            resp = bot.get_response(user_id, domain, user_data)
            
            # Q3: Project Idea
            project = random.choice(PROJECTS)
            resp = bot.get_response(user_id, f"I want to build a {project}", user_data)
            
            # Q4: Programming Confidence (Must be valid)
            conf = random.choice(CONFIDENCE)
            resp = bot.get_response(user_id, conf, user_data)
            
            # Q5: AI Experience
            exp = random.choice(EXPERIENCE)
            resp = bot.get_response(user_id, exp, user_data)
            
            # Q6: Learning Style (Last question triggers save)
            style = random.choice(STYLES)
            resp = bot.get_response(user_id, style, user_data)
            print(f"  Final Response: {resp}")
            
            if "recorded your profile" not in resp:
                print(f"⚠️ Warning: Session {i} might not have finished correctly.")
            else:
                print(f"  ✅ Session {i+1} completed and saved.")
                
        except Exception as e:
            print(f"Error in session {i}: {e}")

    print("\n✅ Data Population Complete!")
    
    if os.path.exists(bot.data_file):
        df = pd.read_excel(bot.data_file)
        print(f"Final data count: {len(df)}")
        print(f"New records added: {len(df) - initial_count}")
    else:
        print("❌ Error: Data file was not created.")

if __name__ == "__main__":
    import os
    import pandas as pd
    populate()
