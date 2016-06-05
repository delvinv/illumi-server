from flask import Flask
from flask_sockets import Sockets
from app import app
import json
import shared_module
sockets = Sockets(app)


@sockets.route('/echo')
def echo_socket(web_socket):
    try:
        while True:
            message = web_socket.receive()
            json_object = json.loads(message)
            ws_username = json_object['pi_incoming_username']
            print "[SOCKET] " + str(ws_username) + " connected."

            if not len(shared_module.connected_clients) > 3:
                shared_module.connected_clients[ws_username] = web_socket
            else:
                print "all 3 books connected!"

    except ValueError:
        print "[SOCKET] JSON Value error.. "
    except TypeError, t:
        print "[SOCKET] JSON Type error.. " + str(t.args)




@app.route('/')
def hello():
    # ws = orra[0]
    # ws.send("Gotcha fool!")
    return 'Hello World! Gotcha'