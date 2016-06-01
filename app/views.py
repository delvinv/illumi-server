from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
UPLOAD_FOLDER = 'uploads/'

# app = Flask(__name__)

from flask_sockets import Sockets
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message)


# Imports for file upload..

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
