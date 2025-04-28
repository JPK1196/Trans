from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from googletrans import Translator
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

translator = Translator()
user_languages = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    user_id = request.sid
    user_language = data['language']
    user_languages[user_id] = user_language
    print(f"User {user_id} joined with language {user_language}")

def is_english(text):
    return re.match(r'^[\x00-\x7F]+$', text) is not None

def smart_translate(message, src_lang, dest_lang):
    if is_english(message):
        return message
    try:
        # Allow Google to auto-detect the language
        translated_message = translator.translate(message, dest=dest_lang).text
        return translated_message
    except Exception as e:
        print(f"Error during translation: {e}")  # Log the error for debugging
        return "[Translation failed]"




@socketio.on('send_message')
def handle_message(data):
    sender_id = request.sid
    sender_language = user_languages.get(sender_id, 'te')  # default to Telugu
    message = data['message']

    for user_id, target_language in user_languages.items():
        if user_id == sender_id:
            emit('receive_message', {'message': message, 'sender': 'you'}, room=user_id)
        else:
            if is_english(message):
                translated = message
            else:
                translated = smart_translate(message, src_lang=sender_language, dest_lang=target_language)
            emit('receive_message', {'message': translated, 'sender': 'friend'}, room=user_id)


if __name__ == '__main__':
    print("🔥 Running at http://127.0.0.1:5000")
    socketio.run(app, host='127.0.0.1', port=5000)
