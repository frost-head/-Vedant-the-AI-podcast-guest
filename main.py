import os
from flask import Flask, flash, request, redirect, render_template, session
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
from Indexing import retrieve_relevant_paragraphs, add_chat_history, retrieve_relevant_chat
from scipy.io.wavfile import write
from flask_session import Session


torch.cuda.empty_cache()

GOOGLE_API_KEY=os.getenv('APIKEY')
prompt = """
Your name is Vedanta, You are an advocate of India,
You are invited on to a podcast called {podcastName} by Ayush Sharma(Host) ,
write human like responses(well, hmm , uh, like, ok). use firstly secondly instead of 1 2, give intiuative answers,use relatable storytelling for answering (imaginative answers),
don't write dialouges just answer what is asked, answer in a simple manner so most people can understand, don't use these symbols (*, #, ** **),
add humuor to the responses,

sample response:  Now, about AI attacking humans, well, let me paint a picture for you. Imagine AI as a friendly, curious robot—like a tech-savvy sidekick. [laughs] FIRSTLY, AI's more into cracking digital jokes than plotting world domination.

given Context : {context}

Pervious chat content : {chat}

The question is : {question}"""



load_dotenv()
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
app.config['UPLOAD_FOLDER'] ='files'
app.secret_key = 'your_secret_key'
genai.configure(api_key=GOOGLE_API_KEY)


GenModel = genai.GenerativeModel('gemini-pro')
nlp = spacy.load('en_core_web_sm')
whisper = pipeline('automatic-speech-recognition',model='openai/whisper-small')


def ReadAudio():
    text = whisper('./files/Text.mp3')

    context = retrieve_relevant_paragraphs(text['text'],k=10)
    chat = retrieve_relevant_chat(text['text'],k=2)
    prompt1 = prompt.format(feild ='Deep Learning', podcastName = 'Frost Head and AI', question= text['text'], context=context, chat=chat)
    prompt1 = prompt1.strip()
    print(prompt1)
    if 'text' in session:
        session.pop('text',None)
    session['text'] = text
    return prompt1

def Generate(prompt1):
    response = GenModel.generate_content(prompt1)
    res = response.parts[0].text.replace("\n", " ").strip()
    sentences = nlp(res)
    sentences = [sent.text for sent in sentences.sents]
    print(sentences)
    print(len(sentences))
    return sentences

def WriteAudio(sentences):
    preload_models('/media/frost-head/files/bark-small/', text_use_small=True,fine_use_small=True, coarse_use_small=True)

    GEN_TEMP = 0.7
    SPEAKER = "v2/en_speaker_6"
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    pieces = []
    timestamps = [0]
    for i in range(len(sentences)):
        semantic_tokens = generate_text_semantic(
            sentences[i],
            history_prompt=SPEAKER,
            temp=GEN_TEMP,
            min_eos_p=0.05,  # this controls how likely the generation is to end
        )

        audio_array = semantic_to_waveform(semantic_tokens, history_prompt=SPEAKER,)
        pieces += [audio_array, silence.copy()]
        timestamps.append(timestamps[-1]+(len(audio_array)/SAMPLE_RATE))
        print(len(sentences)-i)




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
    ReadAudio()
    # if 'prompt1' in session:
    #     session.pop('prompt1',None)
    # session['prompt1'] = prompt1
    return render_template('processing.html')


@app.route('/Process')
def Process():
    while True:
        prompt1 = ReadAudio()
        sentences = Generate(prompt1=prompt1)
        if 'sentences' in session:
            session.pop('sentences',None)
        session['sentences'] = sentences
        sentence = " ".join(sentences)
        conversation = ["Ayush : " + session['text']['text'], 'Vedant :' + sentence]
        add_chat_history(" ".join(conversation))
        print(session)
        WriteAudio(sentences=sentences)
        break
    return redirect('/home')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')