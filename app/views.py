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

# Main page
@app.route('/')
@app.route('/index')
@app.route('/main')
def index():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('index.html', signed_in=signed_in_status)



# TODO: fix this, very similar to index page rendering above..
@app.route('/userHome')
def userHome():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    print "[VIEWS] User login status is: " + str(signed_in_status)
    return render_template('index.html', signed_in=signed_in_status)


@app.route('/error')
def error_page(error_message):
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('error.html', signed_in=signed_in_status)


@app.route('/about')
def about_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('about.html', signed_in=signed_in_status)


@app.route('/installation-instructions')
def install_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('installation-instructions.html', signed_in=signed_in_status)


@app.route('/how-to-use')
def howto_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('how-to-use.html', signed_in=signed_in_status)


@app.route('/about-server')
def aboutserver_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('about-server.html', signed_in=signed_in_status)


@app.route('/about-pi')
def aboutpi_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('about-pi.html', signed_in=signed_in_status)


@app.route('/about-web')
def aboutweb_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('about-web.html', signed_in=signed_in_status)


@app.route('/wooden_book')
def woodenbook_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('wooden_book.html', signed_in=signed_in_status)


@app.route('/contact')
def contact_page():
    if session.get('user'):
        signed_in_status = True
    else:
        signed_in_status = False
    return render_template('contact.html', signed_in=signed_in_status)