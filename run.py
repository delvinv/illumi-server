#!flask/bin/python
from app import app
app.config['DEBUG'] = True
# app.run(debug=True)

from flask_sockets import Sockets
sockets = Sockets(app)
