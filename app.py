import os
import google.generativeai as genai
from flask import Flask, render_template, request, session, jsonify, send_file
from flask_session import Session
import markdown
import json
from datetime import datetime
import io
import re
import markdownify

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Flask-Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set your Gemini API key
genai.configure(api_key=os.environ['GEMINI_API'])

# Initialize stats.txt if it doesn't exist
if not os.path.exists('stats.txt'):
    with open('stats.txt', 'w') as f:
        f.write('0')

# Initialize request_data.json if it doesn't exist
if not os.path.exists('request_data.json'):
    with open('request_data.json', 'w') as f:
        json.dump({"timestamps": [], "counts": [], "user_messages": [], "bot_responses": []}, f)

# Flag to track if the model has responded at least once
model_responded = False

@app.route('/', methods=['GET', 'POST'])
def index():
    global model_responded
    chat_history = session.get('chat_history', [])

    # Set the model_responded flag to True if there is at least one model message in the chat history
    if any(message['role'] == 'model' for message in chat_history):
        model_responded = True

    if request.method == 'POST':
        if 'clear-history' in request.form:
            session['chat_history'] = []
            chat_history = []
            return jsonify({'status': 'success'})
        else:
            user_message = request.form['message']
            user_message_markdown = markdown.markdown(user_message)
            chat_history.append({"role": "user", "parts": [user_message_markdown]})

            # Generate response from Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            chat = model.start_chat(history=chat_history)

            formatted_message = {"role": "user", "parts": [user_message_markdown]}
            response = chat.send_message(formatted_message)

            bot_response = response.text
            bot_response_markdown = markdown.markdown(bot_response)
            chat_history.append({"role": "model", "parts": [bot_response_markdown]})

            session['chat_history'] = chat_history

            # Increment the request count in stats.txt
            with open('stats.txt', 'r+') as f:
                count = int(f.read())
                count += 1
                f.seek(0)
                f.write(str(count))
                f.truncate()

            # Update request_data.json with the new request count and timestamp
            with open('request_data.json', 'r+') as f:
                data = json.load(f)
                data["timestamps"].append(datetime.now().isoformat())
                data["counts"].append(count)
                data["user_messages"].append(user_message)
                data["bot_responses"].append(bot_response)
                f.seek(0)
                json.dump(data, f)
                f.truncate()

            # Set the flag to True when the model responds
            model_responded = True

            return jsonify({'answer': bot_response_markdown})

    chat_history = session.get('chat_history', [])
    return render_template('index.html', chat_history=chat_history, model_responded=model_responded)

@app.route('/stats')
def stats():
    with open('stats.txt', 'r') as f:
        count = f.read()
    with open('request_data.json', 'r') as f:
        data = json.load(f)
    latest_user_messages = data["user_messages"][-5:]
    latest_bot_responses = data["bot_responses"][-5:]
    return render_template('stats.html', count=count, latest_user_messages=latest_user_messages, latest_bot_responses=latest_bot_responses)

@app.route('/request-count')
def request_count():
    with open('stats.txt', 'r') as f:
        count = f.read()
    return jsonify({'count': int(count)})

@app.route('/request-data')
def request_data():
    with open('request_data.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/download-chat-history')
def download_chat_history():
    chat_history = session.get('chat_history', [])
    chat_history_text = "\n".join([f"{msg['role']}: {markdownify.markdownify(msg['parts'][0])}" for msg in chat_history])
    chat_history_io = io.StringIO(chat_history_text)
    return send_file(io.BytesIO(chat_history_io.getvalue().encode()), mimetype='text/plain', as_attachment=True, download_name='chat_history.txt')

@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    chat_history = session.get('chat_history', [])
    chat_history_text = "\n".join([markdownify.markdownify(msg['parts'][0]) for msg in chat_history])

    # Generate summary using Gemini API
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])  # Start a new chat

    # Send a message to Gemini to summarize the chat history
    summary_request = f"Please summarize the following conversation:\n\n{chat_history_text}"
    response = chat.send_message({"role": "user", "parts": [summary_request]})

    summary = response.text

    return jsonify({'summary': summary})

@app.route('/latest-messages')
def latest_messages():
    with open('request_data.json', 'r') as f:
        data = json.load(f)
    latest_user_messages = data["user_messages"][-5:]
    latest_bot_responses = data["bot_responses"][-5:]
    return jsonify({'user_messages': latest_user_messages, 'bot_responses': latest_bot_responses})

if __name__ == '__main__':
    app.run(debug=True)