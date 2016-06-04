import requests
from websocket import create_connection
import json
from random import randint

SERVER_ADDRESS = 'localhost'
SERVER_PORT = '8000'

# random_int = randint(0,9999)
fileRepo = "./fileRepo"
files = {'image_file' : open("image.jpg", 'rb'), 'audio_file' : open('audio.wav', 'rb')}

# IMPORTANT: whisper_id is a pre-existing number associated with already-created whispers on the server, so send me something that i have sent you already...
# Random number used here for testing purposes only!
piid = {'whisper_id' : "29", 'username' : "beargrylls"}
url = 'http://localhost:8000/uploadWhisper'

def PostRequest():
    r = requests.post(url, data=piid, files=files)
    print r.status_code
    print r.text

def ServerWait():
    # full_path = "ws://{}:{}/echo".format(SERVER_ADDRESS, SERVER_PORT)
    # ws = create_connection(full_path)
    ws = create_connection("ws://localhost:8000/echo")

    # When program starts, open a connection and send a websocket packet to server with following command
    message = '{"id": "beargrylls", "name": "delvin_book"}'
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
        result =  ws.recv()
        print "Received '%s'" % result
        result =  ws.recv()



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


PostRequest()
	