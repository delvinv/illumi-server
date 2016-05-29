from flask import Flask, render_template, request, json
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'} #fake user
    print "Hello world in views.py"
    return render_template('index.html', title='Home',user=user)


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp', methods=['POST'])
def signUp():
    # read the incoming values
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # check if fields submitted..
    if _name and _email and _password:
        return json.dumps({'html': '<span>All fields submitted!</span>'})
    else:
        return json.dumps({'html': '<span>Enter all fields please!</span>'})