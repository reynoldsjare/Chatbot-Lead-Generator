from flask import Flask, request, jsonify
import openai
import sqlite3

app = Flask(__name__)

# Set your OpenAI API Key (Get one at platform.openai.com)
openai.api_key = "YOUR_OPENAI_API_KEY" "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"

# Function to save leads in a local database
def save_lead(name, email, message):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leads (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI that assists users and captures lead details."},
            {"role": "user", "content": user_message}
        ]
    )

    bot_reply = response["choices"][0]["message"]["content"]

    # Capture leads if email and name are provided
    if "email" in user_message.lower() and "name" in user_message.lower():
        data = user_message.split("\n")
        name = data[0].split(":")[1].strip()
        email = data[1].split(":")[1].strip()
        issue = data[2].split(":")[1].strip()
        save_lead(name, email, issue)

    return jsonify({"response": bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
