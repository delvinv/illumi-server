from flask import Flask
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

orra = []

@sockets.route('/echo')
def echo_socket(ws):
    orra.append(ws)
    print "Echo reached...."
    print type(ws)
    print str(ws)
    while True:
        message = ws.receive()
        ws.send(message)
        ws.send("Great work buddy..")
        ws.send("love from delvin")
        # ws.send("Exit")

@app.route('/')
def hello():
    ws = orra[0]
    ws.send("Gotcha fool!")
    return 'Hello World! Gotcha'