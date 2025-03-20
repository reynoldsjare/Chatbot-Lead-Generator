from flask import Flask, request, jsonify
import openai
import sqlite3
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Set your OpenAI API Key from environment variables (Never hardcode your API keys)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to save leads in a local database
def save_lead(name, email, message):
    try:
        # Using context manager to ensure the connection is closed properly
        with sqlite3.connect("leads.db") as conn:
            cursor = conn.cursor()
            
            # Ensure leads table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    message TEXT
                )
            ''')
            
            cursor.execute("INSERT INTO leads (name, email, message) VALUES (?, ?, ?)", (name, email, message))
            conn.commit()
        logging.info(f"Lead saved: {name}, {email}")
    except Exception as e:
        logging.error(f"Error saving lead: {e}")
        raise

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    
    if not user_message:
        return jsonify({"response": "Message is required."}), 400
    
    # Make the OpenAI API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that assists users and captures lead details."},
                {"role": "user", "content": user_message}
            ]
        )
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return jsonify({"response": "Error contacting AI service. Please try again later."}), 500
    
    # Get the bot's response
    bot_reply = response["choices"][0]["message"]["content"]

    # Use regex to find name, email, and issue in a more flexible manner
    name_match = re.search(r"Name:\s*(.+)", user_message, re.IGNORECASE)
    email_match = re.search(r"Email:\s*(\S+)", user_message, re.IGNORECASE)
    issue_match = re.search(r"Issue:\s*(.+)", user_message, re.IGNORECASE)

    if name_match and email_match and issue_match:
        name = name_match.group(1).strip()
        email = email_match.group(1).strip()
        issue = issue_match.group(1).strip()
        
        # Save the lead to the database
        try:
            save_lead(name, email, issue)
        except Exception as e:
            return jsonify({"response": f"Error saving lead: {e}"}), 500
    else:
        logging.warning(f"Incomplete lead data: {user_message}")
        return jsonify({"response": "Lead data is incomplete or incorrectly formatted. Please provide Name, Email, and Issue."}), 400

    return jsonify({"response": bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

