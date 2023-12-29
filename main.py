import os
from flask import Flask, flash, request, redirect, render_template, url_for,session
from dotenv import load_dotenv
import pathlib
import textwrap
import google.generativeai as genai
from bark.generation import (
    generate_text_semantic,
    preload_models,
)
from bark.api import semantic_to_waveform
from bark import generate_audio, SAMPLE_RATE
from transformers import pipeline
import torch
import spacy
from bark import SAMPLE_RATE
import numpy as np
from scipy.io.wavfile import write


torch.cuda.empty_cache()

GOOGLE_API_KEY=os.getenv('APIKEY')
prompt = """
Your name is Vedanta, You are a virtual(robot,LLM) expert in {feild} from India,
You are invited on to a podcast called {podcastName},
write human like responses(well, hmm , uh, like, ok). use firstly secondly instead of 1 2, give intiuative answers,use relatable storytelling for answering (imaginative answers),
don't write dialouge just answer what is asked in a simple manner so most people can understand, ,
add humuor to the responses, ... or — for hesitations,use CAPITALIZATION for emphasis of a word instead of ** **,

sample response:  Now, about AI attacking humans, well, let me paint a picture for you. Imagine AI as a friendly, curious robot—like a tech-savvy sidekick. [laughs] FIRSTLY, AI's more into cracking digital jokes than plotting world domination.

The question is {question}
"""



load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] ='files'
app.secret_key = 'your_secret_key'
genai.configure(api_key=GOOGLE_API_KEY)


GenModel = genai.GenerativeModel('gemini-pro')
nlp = spacy.load('en_core_web_sm')
whisper = pipeline('automatic-speech-recognition',model='openai/whisper-small')


def ReadAudio():
    text = whisper('./files/Text.mp3')
    prompt1 = prompt.format(feild ='Deep Learning', podcastName = 'Frost Head and AI', question= text['text'])
    prompt1 = prompt1.strip()
    return prompt1

def Generate(prompt1):
    response = GenModel.generate_content(prompt1)
    res = response.parts[0].text.replace("\n", " ").strip()
    sentences = nlp(res)
    sentences = [sent.text for sent in sentences.sents]
    return sentences

def WriteAudio(sentences):
    preload_models('/media/frost-head/files/bark-small/', text_use_small=True,fine_use_small=True, coarse_use_small=True)

    GEN_TEMP = 0.7
    SPEAKER = "v2/en_speaker_6"
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    pieces = []
    timestamps = [0]
    for sentence in sentences:
        semantic_tokens = generate_text_semantic(
            sentence,
            history_prompt=SPEAKER,
            temp=GEN_TEMP,
            min_eos_p=0.05,  # this controls how likely the generation is to end
        )

        audio_array = semantic_to_waveform(semantic_tokens, history_prompt=SPEAKER,)
        pieces += [audio_array, silence.copy()]
        timestamps.append(timestamps[-1]+(len(audio_array)/SAMPLE_RATE))





    data = np.concatenate(pieces)
    data = np.float32(data / np.max(np.abs(data)))
    write('./static/Text.wav', SAMPLE_RATE, data)
    if 'timestamps' in session:
        session.pop('timestamps',None)
    session['timestamps'] = timestamps


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/save-record', methods=['POST'])
def save_record():
    if 'sentences' in session:
        session.pop('sentences',None)
    if 'timestamps' in session:
        session.pop('timestamps',None)
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
    return '/Processing'

@app.route('/Processing')
def Processing():
    return render_template('processing.html')


@app.route('/Process')
def Process():
    while True:
        prompt1 = ReadAudio()
        sentences = Generate(prompt1=prompt1)
        if 'sentences' in session:
            session.pop('sentences',None)
        session['sentences'] = sentences

        WriteAudio(sentences=sentences)
        break
    return redirect('/home')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')