from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
from werkzeug import generate_password_hash, check_password_hash
from .. import connect_db

import logging
logging.basicConfig(filename='logs/illumi_users.log',level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/register', methods=['POST', 'GET'])
@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    if request.method == "POST":
        # read the incoming values
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # check if fields submitted..
        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            db_result = connect_db.signup_to_database(_name, _email, _hashed_password)
            print "DB_Result = " + str(db_result)
            output = connect_db.validate_email(_email)
            if output:
                session['user'] = output[0]
                session['user_email'] = _email
            return redirect('/userHome')
            # return json.dumps({'message':'User created successfully !'})
        else:
            return json.dumps({'html': '<span>Enter all fields please!</span>'})
    return render_template("signup.html")


# @app.route('/showSignIn')
# def showSignIn():
#     return render_template('signin.html')

@app.route('/login', methods=['POST', 'GET'])
@app.route('/showSignIn', methods=['POST', 'GET'])
@app.route('/signIn', methods=['POST', 'GET'])
def signIn():
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
                    session['user_email'] = _email
                    print session['user']
                    return redirect('userHome')
                else:
                    return render_template('error.html', error="Password check failed!")
            else:
                return render_template('error.html', error="user does not exist!")
        else:
            return render_template('error.html', error="Both fields required..")
    return render_template('signin.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')

