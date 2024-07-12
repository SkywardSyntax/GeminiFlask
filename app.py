import os
import pathlib
import uuid

import google.generativeai as genai
from flask import Flask, render_template, request, session, jsonify

genai.configure(api_key="YOUR_GEMINI_API_KEY")  

app = Flask(__name__)
app.secret_key = os.urandom(24)

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def process_directory(directory, base_path=""):
    file_data = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        rel_path = os.path.join(base_path, item)

        if os.path.isfile(item_path):
            try:
                with open(item_path, "rb") as file:
                    mime_type = "text/plain"
                    if item_path.endswith((".jpg", ".jpeg", ".png")):
                        mime_type = "image/jpeg"
                    file_data.append({
                        "mime_type": mime_type,
                        "data": file.read(),
                        "path": rel_path
                    })
                print(f"DEBUG: Uploaded '{rel_path}' successfully")
            except Exception as e:
                print(f"DEBUG: Error uploading '{rel_path}': {e}")
        elif os.path.isdir(item_path):
            file_data.extend(process_directory(item_path, rel_path))
    return file_data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "directory" not in session:
            session["directory"] = str(uuid.uuid4())

        directory_id = session.get('directory')
        upload_path = os.path.join('uploads', directory_id)
        os.makedirs(upload_path, exist_ok=True)

        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            file_path = os.path.join(upload_path, file.filename)
            file.save(file_path)
            print(f"DEBUG: Saved '{file.filename}' to '{file_path}'")

        all_context = process_directory(upload_path)
        session['context'] = all_context

        # Start a new chat session and set context
        chat_session = model.start_chat()
        session['chat_history'] = []

        # Format the initial message and context
        initial_message = "Use these files as context for future questions:\n"
        for file_info in all_context:
            initial_message += f"- {file_info['path']}\n"
        gemini_context = all_context # The context is already in the correct format

        try:
            response = chat_session.send_message(initial_message, context=gemini_context)
            print(f"DEBUG: Gemini initial response: {response.text}")

            session['chat_history'].append({
                'role': 'user',
                'content': initial_message
            })
            session['chat_history'].append({
                'role': 'model',
                'content': response.text
            })
            print("DEBUG: Chat History:", session['chat_history'])

        except Exception as e:
            return jsonify({'message': f"Error setting context with Gemini: {e}"}), 500

        return jsonify({'message': 'Directory uploaded, processed, and context set with Gemini!'}), 200

    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get('message')
    context = session.get('context', [])
    chat_history = session.get('chat_history', [])

    # Recreate ChatSession from history
    chat_session = model.start_chat(history=chat_history)

    try:
        # Send the user message with context
        chat_message = f"Considering the files you have been provided, {user_message}"
        response = chat_session.send_message(chat_message, context=context)  

        chat_history.append({
            'role': 'user',
            'content': user_message
        })
        chat_history.append({
            'role': 'model',
            'content': response.text
        })
        session['chat_history'] = chat_history
        print("DEBUG: Chat History:", session['chat_history'])

        return response.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)