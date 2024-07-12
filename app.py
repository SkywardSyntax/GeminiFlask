import os
import google.generativeai as genai
from flask import Flask, render_template, request, session, jsonify

genai.configure(api_key="AIzaSyADryF7SSQmH2YA3VrVPG2No_9OZQaGXM0")

app = Flask(__name__)
app.secret_key = os.urandom(24)

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

@app.route("/", methods=["GET"])  # Only GET for now
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def start_chat():
    try:
        # Hardcode a simple text context for testing 
        context_text = "The quick brown fox jumps over the lazy dog." 
        session['chat'] = model.start_chat(context=[{'text': context_text}])

        return jsonify({'message': 'Chat session started with context!'}), 200

    except Exception as e:
        return jsonify({'message': f"Error starting chat: {e}"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get('message')
    chat_session = session.get('chat')

    if not chat_session:
        return jsonify({'error': 'No chat session found. Please start a chat first.'}), 400

    try:
        response = chat_session.send_message(user_message)
        return response.text

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)