from websocket import create_connection
import json

SERVER_ADDRESS = 'localhost'
SERVER_PORT = '8000'
PI_USERNAME = "janeeyre"
# full_path = "ws://{}:{}/echo".format(SERVER_ADDRESS, SERVER_PORT)
# ws = create_connection(full_path)
SOCKET_CONNECTION_URL = "ws://localhost:8000/echo"
ws = create_connection(SOCKET_CONNECTION_URL)

# When program starts, open a connection and send a websocket packet to server with following command
message = '{"whisper_id": "9845723958", "username": "janeeyre"}'
print "Sending " + message
ws.send(message)

# Now wait till you receive a message from the server (using a while loop).
# The message will be a string but it contains JSON data:
# {
#     'image_url': 'http://www.example.com:5000/uploads/654f80d1b3b848518dd5d5cf808fa857.png',
#     'audio_url': 'http://www.example.com:5000/uploads/654f80d1b3b848518dd5d5cf808fa857.wav',
#     'timestamp': '2016-06-02 04:38:50'
# }
# Basically, use the json module to convert the string into a JSON object. Then get the audio and image from
# the URLs given. This can be done as done here: http://stackoverflow.com/a/19602990/1341215

while True:
    try:
        result =  ws.recv()
        print "Received '%s'" % result
        result =  ws.recv()
    except KeyboardInterrupt:
        print "Stopped manually..."
    except Exception, e:
        print e.message
        ws = create_connection(SOCKET_CONNECTION_URL)
        ws.send("[SOCKET] " + PI_USERNAME + " connection restablished...")
        print("[SOCKET] " + PI_USERNAME + " connection restablished...")




        # Opening a websocket connection:
        # ws = create_connection("ws://localhost:8000/echo")

        # Sending a packet to the server
        # ws.send("Hello Server")

        # Receiving a packet from the server. Keep this running forever to ensure push notifications are received...
        # result =  ws.recv()

        # Closing a websocket connection:
        # ws.close()

# Sending files back to the server: Use REQUESTS and send information required by the main form in the server to start a whisper...
# http://docs.python-requests.org/en/master/