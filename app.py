from flask import Flask, render_template, request, session, jsonify, send_file
from openai import OpenAI
import sounddevice as sd
import soundfile as sf
from gtts import gTTS
import os
from scipy.io.wavfile import write
from typing import Union
from werkzeug.datastructures import FileStorage
import config
import uuid


app = Flask(__name__)
app.secret_key = os.urandom(24)

# OpenAI クライアント（新SDK）
client = OpenAI(api_key=config.OPENAI_API_KEY)

DURATION = 30  # 録音時間（秒）
SAMPLE_RATE = 44100  # サンプリングレート

def record_audio():
    print("録音を開始します。話しかけてください...")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float64')
    sd.wait()
    write('output.wav', SAMPLE_RATE, audio_data)
    print("録音が完了しました。")
    return 'output.wav'

def transcribe_audio(file_input: Union[str, os.PathLike, FileStorage, bytes]):
    # 1) 文字列パス or PathLike
    if isinstance(file_input, (str, os.PathLike)):
        with open(file_input, "rb") as f:
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
            return resp.text

    # 2) Flask の FileStorage（例: request.files["audio"]）
    if hasattr(file_input, "stream"):  # FileStorage想定
        fs: FileStorage = file_input
        try:
            fs.stream.seek(0)
        except Exception:
            pass
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=(fs.filename or "audio.wav", fs.stream, getattr(fs, "mimetype", None) or "audio/wav")
        )
        return resp.text

    # 3) bytes
    if isinstance(file_input, (bytes, bytearray)):
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", bytes(file_input))
        )
        return resp.text

    raise TypeError(f"Unsupported file_input type: {type(file_input)}")

def generate_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o",   # 軽量版。必要なら "gpt-4o" や "gpt-4" に変更可
        messages=messages
    )
    return response.choices[0].message.content

def generate_audio(text):
    filename = f"response_{uuid.uuid4()}.mp3"  # 一意なファイル名を生成
    tts = gTTS(text=text, lang='ja')
    tts.save(filename)
    return filename

@app.route('/')
def home():
    # セッションから会話履歴を削除
    session.pop('conversation', None)

    # 生成された音声ファイルを削除
    audio_files = os.listdir('.')  # カレントディレクトリのファイルをリストアップ
    for file in audio_files:
        if file.endswith('.mp3') or file.endswith('.wav'):  # 音声ファイルを条件に削除
            os.remove(file)

    return render_template('index.html')

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    audio_file = record_audio()
    user_text = transcribe_audio(audio_file)

    # 初回システムメッセージ設定
    if 'conversation' not in session:
        session['conversation'] = [{"role": "system", "content": "あなたは丁寧で親しみやすく、女性的な言葉遣いで応答するカウンセラーです。"}]
    
    # ユーザーの入力を会話に追加
    session['conversation'].append({"role": "user", "content": user_text})
    
    # AIの応答生成
    ai_response = generate_response(session['conversation'])
    audio_path = generate_audio(ai_response)  # 音声ファイル生成

    # AIの応答を会話に追加
    session['conversation'].append({"role": "assistant", "content": ai_response, "audio_path": audio_path})
    
    return render_template('result.html', conversation=session['conversation'])

@app.route('/followup', methods=['POST'])
def followup():
    audio_file = record_audio()
    followup_question = transcribe_audio(audio_file)

    session['conversation'].append({"role": "user", "content": followup_question})
    ai_response = generate_response(session['conversation'])
    audio_path = generate_audio(ai_response)  # 音声ファイル生成
    
    session['conversation'].append({"role": "assistant", "content": ai_response, "audio_path": audio_path})

    return jsonify({"user_text": followup_question, "ai_response": ai_response, "audio_path": audio_path})

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_file(filename, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)