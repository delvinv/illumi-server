from flask import Flask, render_template, request, json, redirect
from app import app
from werkzeug import generate_password_hash, check_password_hash
import connect_db


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


@app.route('/signUp', methods=['POST'])
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
        return json.dumps({'message':'User created successfully !'})
    else:
        return json.dumps({'html': '<span>Enter all fields please!</span>'})


@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

@app.route('/signIn', methods=['POST'])
def signIn():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        if _email and _password:
            output = connect_db.validate_email(_email)
            if len(output) > 0:
                if check_password_hash(str(output[0][3]), _password):
                    return redirect('/userHome')
                else:
                    return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/userHome')
def userHome():
    return render_template('userHome.html')