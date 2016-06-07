from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
# Imports for file upload..
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['mov', 'webm', 'mp4', 'avi', 'wmv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/startWhisper')
def startWhisper():
    if session.get('user'):
        return render_template('old/start_whisper.html')
    else:
        return render_template('old/error.html', error="Unauthorized access!")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploadWhisper', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if file is present in the POST
        if 'file' not in request.files:
            flash('No file part...')
            return redirect(request.url)
        file = request.files['file']
        # if user has not selected file, browser will also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('startWhisper')