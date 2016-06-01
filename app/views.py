from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
from werkzeug import generate_password_hash, check_password_hash
import connect_db

# app = Flask(__name__)

from flask_sockets import Sockets
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)


# Imports for file upload..
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
UPLOAD_FOLDER = 'uploads/'

app.secret_key = 'this is my secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
@app.route('/index')
@app.route('/main')
def index():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        print "Hello world in views.py"
        return render_template('index.html', title='Home')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error="Unauthorized access!")


@app.route('/error')
def error_page(error_message):
    return render_template('error.html', error=error_message)


@app.route('/startWhisper')
def startWhisper():
    if session.get('user'):
        return render_template('start_whisper.html')
    else:
        return render_template('error.html', error="Unauthorized access!")


@app.route('/uploadWhisper', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if file is present in the POST
        if 'file' not in request.files:
            print "No file part..."
            flash('No file part...')
            return redirect('/startWhisper')
        file = request.files['file']
        file_2 = request.files['audio_file']
        print str(file_2)
        print "File found?..."
        # if user has not selected file, browser will also submit an empty part without filename.
        if file.filename == '':
            print "No file file....."
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filename_2 = secure_filename(file_2.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_2))
            print "Bingo!..."
            print str(filename)
            print str(file.filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('userHome.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)