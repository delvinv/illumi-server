import requests
from websocket import create_connection
import json

SERVER_ADDRESS = 'localhost'
SERVER_PORT = '8000'

fileRepo = "./fileRepo"
files = {'image_file' : open(fileRepo+"/image.jpg", 'rb'), 'audio_file' : open(fileRepo+'/audio.wav', 'rb')}
piid = {'whisper_name' : "beargrylls", 'username' : "delvin_book"}
url = 'http://192.168.1.134:8000/uploadWhisper'

def PostRequest():
	r = requests.post(url, data=piid, files=files)
	print r.status_code

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
	