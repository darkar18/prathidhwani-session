from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from agents.chatbot import WarmUpBot
from agents.analytics import AnalyticsAgent
from agents.writer import WriterAgent

app = Flask(__name__)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize Agents
bot = WarmUpBot()
analytics_agent = AnalyticsAgent()
writer_agent = WriterAgent(output_file='static/audience_report.txt')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    user_data = data.get('user_data')
    # Simple user ID simulation (IP address or session cookie would be better in prod)
    user_id = request.remote_addr 
    
    response = bot.get_response(user_id, user_message, user_data)
    return jsonify({"response": response})

@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')

@app.route('/api/admin/chat', methods=['POST'])
def admin_chat():
    data = request.json
    question = data.get('question')
    # Use a static thread_id for the single admin user for now
    answer = analytics_agent.query(question, thread_id="admin_dashboard")
    return jsonify({"answer": answer})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # 1. Analyze data
    analytics_results = analytics_agent.analyze()
    
    # 2. Write report
    report = writer_agent.write_report(analytics_results)
    
    return jsonify({
        "analytics": analytics_results,
        "report": report
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    # Clear data for demo purposes
    if os.path.exists('data/responses.xlsx'):
        os.remove('data/responses.xlsx')
    if os.path.exists('data/audience_report.txt'):
        os.remove('data/audience_report.txt')
    bot.sessions.clear()
    return jsonify({"status": "reset"})

if __name__ == '__main__':
    app.run(debug=True, port=5000,host="0.0.0.0")
