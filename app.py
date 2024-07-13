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

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_context_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.txt'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                session['context_file'] = file.filename  # Store the file name in the session
                print("Context file loaded:", session.get('context_file'))
                # Start a new chat session with the context file as the first message
                model = genai.GenerativeModel('gemini-1.5-flash')
                chat = model.start_chat(history=[{'role': 'user', 'parts': [load_context_from_file(file_path)]}])
                session['chat'] = chat
                print("Chat session started:", session.get('chat'))
        elif 'question' in request.form:
            print("Session in question handling:", session)
            question = request.form['question']
            chat = session.get('chat')
            print("Chat session:", chat)
            
            if chat:
                response = chat.send_message(question)
                answer = response.text
                return answer
            else:
                return "Please upload a context file first."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)