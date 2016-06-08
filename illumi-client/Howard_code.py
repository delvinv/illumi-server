import requests
from websocket import create_connection
import json, time
import sys

print "Username is: " + str(sys.argv[1])
PI_USERNAME = str(sys.argv[1])
SOCKET_CONNECTION_URL = "ws://illumi.delv.in:5000/echo"
ws = create_connection(SOCKET_CONNECTION_URL)


# IMPORTANT: whisper_id is a pre-existing number associated with already-created whispers on the server, so send me something that i have sent you already...
# Random number used here for testing purposes only!
def PostRequest(whisper_id):
    files = {'image_file' : open("image.jpg", 'rb'), 'audio_file' : open('audio.mp3', 'rb')}
    piid = {'whisper_id': whisper_id, 'username': PI_USERNAME}
    url = 'http://illumi.delv.in:5000/uploadWhisper'
    # print "[SOCKET]: " + "sending files using http.."
    r = requests.post(url, data=piid, files=files)
    print r.status_code
    print r.text


def ServerWait():
    ws = create_connection(SOCKET_CONNECTION_URL)

    # When program starts, open a connection and send a websocket packet to server with following command
    # IMPORTANT: whisper_id is a pre-existing number associated with already-created whispers on the server,
    # so send me something that i have sent you already...
    message = {"pi_incoming_username": PI_USERNAME}
    message_str = json.dumps(message)
    print "Sending " + message_str
    ws.send(message_str)

    while True:
        try:
            result =  ws.recv()
            print "Received '%s'" % result
            json_object = json.loads(result)
            whisper_id = json_object['whisper_id']
            PostRequest(whisper_id)
        except KeyboardInterrupt:
            exit()
            break
        except Exception, e:
            print e.message
            print "Reconnecting in 30 seconds.."
            time.sleep(10)
            ws = create_connection(SOCKET_CONNECTION_URL)
            ws.send(message_str)
            print("[SOCKET] " + PI_USERNAME + " connection restablished...")
    #

    # Now wait till you receive a message from the server (using a while loop).
    # The message will be a string but it contains JSON data:
    # {
    #     'image_url': 'http://www.example.com:5000/uploads/654f80d1b3b848518dd5d5cf808fa857.png',
    #     'audio_url': 'http://www.example.com:5000/uploads/654f80d1b3b848518dd5d5cf808fa857.wav',
    #     'timestamp': '2016-06-02 04:38:50'
    # }
    # Basically, use the json module to convert the string into a JSON object. Then get the audio and image from
    # the URLs given. This can be done as done here: http://stackoverflow.com/a/19602990/1341215




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


ServerWait()
	