from flask import Flask
from flask_sockets import Sockets
from app import app
import json
import shared_module
sockets = Sockets(app)


@sockets.route('/echo')
def echo_socket(web_socket):
    try:
        message = web_socket.receive()
        print message
        json_object = json.loads(message)
        ws_username = json_object['username']
    except ValueError:
        print "[SOCKET] JSON decoding error.. "

    print "Username is "+ ws_username

    if not len(shared_module.connected_clients) > 3:
        shared_module.connected_clients[ws_username] = web_socket
    else:
        print "all 3 books connected!"
    while True:
        message = web_socket.receive()
        web_socket.send(message)
        # web_socket.send("Exit")



@app.route('/')
def hello():
    # ws = orra[0]
    # ws.send("Gotcha fool!")
    return 'Hello World! Gotcha'