import os
import google.generativeai as genai
from flask import Flask, render_template, request, session, jsonify
from flask_session import Session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Flask-Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set your Gemini API key
genai.configure(api_key="")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        if 'message' in data:
            message = data['message']
            chat_history = session.get('chat_history', [])  # Get history from session

            # Start a new chat if no history exists
            if not chat_history:
                model = genai.GenerativeModel('gemini-1.5-flash')
                chat = model.start_chat(history=[])
            else:
                # Reconstruct chat from history (you'll need to implement this)
                model = genai.GenerativeModel('gemini-1.5-flash')
                chat = model.start_chat(history=chat_history)  

            response = chat.send_message(message)
            answer = response.text

            # Update chat history
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": answer})
            session['chat_history'] = chat_history  # Store updated history

            return jsonify({'answer': answer})
    return render_template('index.html')

@app.route('/chat-history', methods=['GET'])
def chat_history():
    chat_history = session.get('chat_history', [])
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)
