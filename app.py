import os
import pathlib
import uuid

import google.generativeai as genai
from flask import Flask, render_template, request, session, jsonify

genai.configure(api_key="")

app = Flask(__name__)
app.secret_key = os.urandom(24)

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def process_directory(directory, base_path=""):
    file_uris = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        rel_path = os.path.join(base_path, item)

        if os.path.isfile(item_path):
            try:
                # Upload file using Gemini File API
                uploaded_file = genai.upload_file(path=item_path, mime_type='text/plain')
                file_uris.append({
                    "uri": uploaded_file.uri,
                    "path": rel_path
                })
                print(f"DEBUG: Uploaded '{rel_path}' to '{uploaded_file.uri}'")
            except Exception as e:
                print(f"DEBUG: Error uploading '{rel_path}': {e}")
        elif os.path.isdir(item_path):
            file_uris.extend(process_directory(item_path, rel_path))
    return file_uris

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

        file_uris = process_directory(upload_path)
        session['context'] = file_uris

        # Start a new chat session and set context
        session['chat_history'] = []
        gemini_context = [{'uri': uri['uri']} for uri in file_uris]

        try:
            initial_message = "Use these files as context for future questions:\n"
            for file_info in file_uris:
                initial_message += f"- {file_info['path']} (URI: {file_info['uri']})\n"

            # Create a temporary ChatSession for setting the initial context
            temp_chat_session = model.start_chat()
            response = temp_chat_session.send_message(initial_message, context=gemini_context)
            print(f"DEBUG: Gemini initial response: {response.text}")

            # Save only the initial user message to chat history
            session['chat_history'].append({
                'role': 'user',
                'content': initial_message
            })
            print("DEBUG: Chat History:", session['chat_history'])

        except Exception as e:
            return jsonify({'message': f"Error setting context with Gemini: {e}"}), 500

        return jsonify({'message': 'Directory uploaded, processed, and context set with Gemini!'}), 200

    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get('message')
    file_uris = session.get('context', [])
    chat_history = session.get('chat_history', [])

    # Recreate ChatSession from history (NOT NEEDED ANYMORE)
    #chat_session = model.start_chat(history=chat_history) 

    gemini_context = [{'uri': uri['uri']} for uri in file_uris]
    full_message = f"""Considering the files you have been provided, {user_message}""" # The complete message including context

    try:
        response = model.generate_content(gemini_context + [full_message]) 

        return response.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)