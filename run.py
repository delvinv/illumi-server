#!flask/bin/python
from app import app
app.config['DEBUG'] = True
# app.run(host='0.0.0.0') #debug=True
app.run(debug=True) #debug=True

# from flask_sockets import Sockets
# sockets = Sockets(app)