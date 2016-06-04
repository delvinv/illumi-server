Contains the server code for illumi, the "research chinese whispers" project that connects researchers with older citizens. Developed in Flask & Python... Technologies for Digital Civics project for Dan Howard, Jen Manuel and Delvin Varghese.


Functionality supported: 

- Creating a user account 

- Logging in with existing user account 

- Starting a Chinese whisper by uploading image/audio files through the server.. 

- The whisper is then forwarded through a series of connected clients. The order is randomised for each project. 

- Developed with scale in mind. Support multiple users, multiple projects, and multiple clients (not just a works for a demo project).. 

- Researcher can track the status of the whisper and the files sent back by the clients using the web interface.. 

- Server emails the researcher when the final Pi sends back their "whisper"


Developed using:
- Flask (a Python web framework) 
- Jinja (frontend templating package)
- Bootstrap (frontend design)
- MySQL (database storage)


API: 

# Connect to Digital Civics wifi

## Pi establishing connection with server: 

from websocket import create_connection
PI_USERNAME = "janeeyre"
SOCKET_CONNECTION_URL = "ws://gooseberry/echo"
ws = create_connection(SOCKET_CONNECTION_URL)

Socket registration by sending this JSON (username is the important bit): 
message = '{"whisper_id": "9845723958", "username": PI_USERNAME}'
ws.send(message)

Currently, server has accounts for 3 usernames: 
- conandoyle
- janeeyre
- beargrylls

Also remember to keep an open connection to receive notfications from the server: 

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

## PI sending files

Using requests.POST
    files = {'image_file' : open("image.jpg", 'rb'), 'audio_file' : open('audio.wav', 'rb')}
    piid = {'whisper_id' : "29", 'username' : "beargrylls"}
    url = 'http://gooseberry/uploadWhisper'
    r = requests.post(url, data=piid, files=files)
    
    
## Receiving Files

Server will send a JSON string when new files are available for a particular PI. The JSON will look like the following: 
    '{"audio_url": "http://gooseberry/uploads/79803a0c0d0541a695cd248d21941532.wav", 
        "image_url": "http://gooseberry/uploads/79803a0c0d0541a695cd248d21941532.jpg", "project_id": "29"}'

This can be then parsed and downloaded from the provided URL..
