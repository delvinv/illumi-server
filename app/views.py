from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
from werkzeug import generate_password_hash, check_password_hash
import connect_db

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
ALLOWED_EXTENSIONS = set(['mov', 'webm', 'mp4', 'avi', 'wmv'])

app.secret_key = 'this is my secret key'
# app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/index')
@app.route('/main')
def index():
    user = {'nickname': 'Miguel'} #fake user
    print "Hello world in views.py"
    return render_template('index.html', title='Home',user=user)


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    # read the incoming values
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # check if fields submitted..
    if _name and _email and _password:
        _hashed_password = generate_password_hash(_password)
        db_result = connect_db.signup_to_database(_name, _email, _hashed_password)
        print db_result
        return redirect('/userHome')
        # return json.dumps({'message':'User created successfully !'})
    else:
        return json.dumps({'html': '<span>Enter all fields please!</span>'})


@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')


@app.route('/signIn', methods=['POST', 'GET'])
def signIn():
    print "Hello world"
    # All done inside the form
    if request.method == "POST":
        # TODO: validate input
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        if _email and _password:
            output = connect_db.validate_email(_email)
            if len(output) > 0:
                if check_password_hash(str(output[0][3]), _password):
                    session['user'] = output[0][0]
                    return redirect('userHome')
                else:
                    return render_template('error.html', error="Password check failed!")
            else:
                return render_template('error.html', error="user does not exist!")
        else:
            return render_template('error.html', error="Both fields required..")
    return render_template('signin.html')


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error="Unauthorized access!")


@app.route('/error')
def error_page(error_message):
    return render_template('error.html', error=error_message)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')


@app.route('/startWhisper')
def startWhisper():
    if session.get('user'):
        return render_template('start_whisper.html')
    else:
        return render_template('error.html', error="Unauthorized access!")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploadWhisper', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if file is present in the POST
        if 'file' not in request.files:
            print "No file part..."
            flash('No file part...')
            return redirect('/startWhisper')
        file = request.files['file']
        print "File found?..."
        # if user has not selected file, browser will also submit an empty part without filename.
        if file.filename == '':
            print "No file file....."
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print "Bingo!..."
            print str(filename)
            print str(file.filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('userHome.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)