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

# Initialize stats.txt if it doesn't exist
if not os.path.exists('stats.txt'):
    with open('stats.txt', 'w') as f:
        f.write('0')

@app.route('/', methods=['GET', 'POST'])
def index():
    chat_history = session.get('chat_history', [])

    if request.method == 'POST':
        if 'clear-history' in request.form:
            session['chat_history'] = []
            chat_history = []
            return jsonify({'status': 'success'}) 
        else:
            user_message = request.form['message']
            chat_history.append({"role": "user", "parts": [user_message]})

            # Generate response from Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            chat = model.start_chat(history=chat_history)

            formatted_message = {"role": "user", "parts": [user_message]} 
            response = chat.send_message(formatted_message)

            bot_response = response.text
            chat_history.append({"role": "model", "parts": bot_response})

            session['chat_history'] = chat_history

            # Increment the request count in stats.txt
            with open('stats.txt', 'r+') as f:
                count = int(f.read())
                count += 1
                f.seek(0)
                f.write(str(count))
                f.truncate()

            return jsonify({'answer': bot_response})  

    # Removed the code that added the initial "Hi" message

    return render_template('index.html', chat_history=chat_history)

@app.route('/stats')
def stats():
    with open('stats.txt', 'r') as f:
        count = f.read()
    return render_template('stats.html', count=count)

if __name__ == '__main__':
    app.run(debug=True)
