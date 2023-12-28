import os
import uuid
from flask import Flask, flash, request, redirect, send_file, jsonify, Response
from scipy.io import wavfile
from flask_cors import CORS, cross_origin
import pyaudio
from wave import open as wave_open  # Import wave module for reading audio files

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] ='files'
CORS(app, resources={r"/Audio/*": {"origins": "*"}})

import base64
@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    file_name = "Text.mp3"            #str(uuid.uuid4()) + ".mp3"
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(full_file_name)
    return '<h1>Success</h1>'



FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

audio_stream = pyaudio.PyAudio()


def read_audio_file(filename):
    """Reads audio data from a WAV file."""
    with wave_open(filename, "rb") as wav_file:
        wav_header = wav_file.readframes(wav_file.getnframes())  # Read entire WAV header
        while True:
            data = wav_file.readframes(CHUNK)  # Read audio data in chunks
            if not data:
                break  # Stop reading when EOF is reached
            yield wav_header + data  # Yield header and data together


@app.route("/audio")
def audio():
    return Response(read_audio_file("static/Text.wav"))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded = True)