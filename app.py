import os
import google.generativeai as genai
from flask import Flask, render_template, request, session
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
    chat_history = session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.form['message']
        chat_history.append({"role": "user", "parts": [user_message]})

        # Generate response from Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat(history=chat_history)

        # Correctly formatted message for send_message
        formatted_message = {"role": "user", "parts": [user_message]} 
        response = chat.send_message(formatted_message)

        bot_response = response.text
        chat_history.append({"role": "model", "parts": bot_response})

        session['chat_history'] = chat_history

        return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)