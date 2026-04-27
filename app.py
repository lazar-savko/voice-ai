import os
from flask import Flask, request, send_file, render_template, jsonify
from gtts import gTTS
from io import BytesIO
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
MODEL_NAME = "gemini-3-flash-preview"

def text_to_audio_file(text):
    tts = gTTS(text)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file


def ask_question(content):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable")

    question_content = (
        f"{content}. Please answer in a silly way. "
        "answer like a baby"
    )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=question_content
    )
    print(response.text)
    return response.text
# ask_question("how are you?")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speak', methods=['POST'])
def speak():
    sentence = request.form.get('sentence')
    print(sentence)
    print(type(sentence))

    if not sentence:
        return {"error": "Please provide a sentence"}, 400
    try:
        answer = ask_question(sentence)
    except Exception as exc:
        return jsonify({"error": f"AI service error: {exc}"}), 502

    if not answer:
        return jsonify({"error": "AI returned an empty answer"}), 502

    audio_file = text_to_audio_file(answer)
    return send_file(audio_file, mimetype='audio/mpeg')


if __name__ == '__main__':
    app.run(debug=True)