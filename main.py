import os
import uuid
from flask import Flask, flash, request, redirect, send_file, json, Response,jsonify
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] ='files'

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


# @app.route("/audio")
# def audio():
#     filename = "static/Text.wav"  # Replace with actual filename

#     # Read the content of the audio file
#     with open(filename, "rb") as file:
#         audio_content = file.read()

#     # Set the appropriate headers for the response
#     response_headers = {
#         "Content-Type": "audio/wav",
#         "Content-Disposition": f"attachment; filename={filename}",
#     }

#     # Return the complete content of the audio file as a response
#     return jsonify({'':audio_content, '':200, '':response_headers})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded = True)