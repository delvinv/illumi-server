from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import datetime
from .. import connect_db
import shared_module
from random import shuffle

import uuid
uuid_generator = uuid.uuid4()

WEB_URL = "http://192.168.1.149/"
UPLOAD_FOLDER = 'uploads/'


@app.route('/startWhisper')
def startWhisper():
    if session.get('user'):
        return render_template('start_whisper.html')
    else:
        return render_template('error.html', error="Unauthorized access!")


# We need to find what devices are available and shuffle them each time a new whisper is started!
# Then it is stored in the database so that the whisper can be spread in the right order.
#   time to shuffle and push to shared_module..
def create_shuffled_list(whisper_id):
    keys_order = list(shared_module.connected_clients.keys())
    if len(keys_order) == 0:
        return None
    else:
        shuffle(keys_order)
        return keys_order


def convert_keys_to_json(keys_order):
    # Generate JSON of this shuffled order
    json_object = []
    for key in keys_order:
        inner_dict = {key:"False"}
        json_object.append(inner_dict)
    json_string = json.dumps(json_object)
    print "JSON IS: "+ json_string
    return json_string


def save_file_and_return_url(file_sent, file_suffix):
    # Get the file extensions
    image_extension = os.path.splitext(file_sent.filename)[1]
    final_file = WEB_URL + UPLOAD_FOLDER + file_suffix + image_extension

    # Save the files to disk.
    file_sent.save(os.path.join(app.config['UPLOAD_FOLDER'], final_file))
    print "[STATUS] Files generated: " + str(final_file)

    return final_file


@app.route('/uploadWhisper', methods=['POST', 'GET'])
def upload_file():
    print "[" + request.method + "] Request.. "
    if request.method == 'POST':
        # check if file is present in the POST
        if 'audio_file' not in request.files:
            print "No file part..."
            flash('No file part...')
            return redirect('/startWhisper'), 400
        else:
            print "[STATUS] Valid file "
        image_file = request.files['image_file']
        print "[STATUS] Valid images "
        audio_file = request.files['audio_file']
        print "[STATUS] Valid audio "
        whisper_title = request.form['whisper_title']
        print "[STATUS] Valid whisper_title "
        username = request.form['username']
        print "[STATUS] Files found for..."+str(username) + " (" + image_file.filename + ")"

        # if user has not selected file, browser will also submit an empty part without filename.
        if image_file.filename == '' or audio_file.filename == '':
            print "No file selected bro....."
            flash('No selected file')
            return redirect(request.url), 400
        else:
            # Generate a uuid and save this image/audio as that name..
            gen_filename = uuid_generator.hex
            form_image_url = save_file_and_return_url(image_file, gen_filename)
            form_audio_url = save_file_and_return_url(audio_file, gen_filename)

            current_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
            # username = session['user']
            whisper_id = connect_db.add_new_whisper(username, whisper_title, current_timestamp)
            audio_to_db = connect_db.add_file_details_to_db(form_audio_url,whisper_id,"audio",username,current_timestamp)
            image_to_db = connect_db.add_file_details_to_db(form_image_url,whisper_id,"image",username,current_timestamp)
            if audio_to_db and image_to_db:
                print "[STATUS] files saved to database.."

            # if the form is posted from a browser, we can assume that it is a researcher sharing their content
            # and start the whisper process.
            shuffled_list = None
            # TODO: check instead if username is a researcher or participant...
            if 'user' in session:
                shuffled_list = create_shuffled_list(whisper_id)
                if shuffled_list is not None:
                    json_string = convert_keys_to_json(shuffled_list)
                    # post this shuffled order to the database...
                    op_output = connect_db.add_json_status_to_db(json_string, whisper_id)
                    print "DB operation for storing shuffle was: " + str(op_output)
                    next_item = shuffled_list[-1]
                    web_socket = shared_module.connected_clients[next_item]
                    json_obj = {
                        "audio_url":form_audio_url,
                        "image_url":form_image_url,
                        "project_id":"24"
                    }
                    json_string = json.dumps(json_obj)
                    web_socket.send(json_string)
                    print "Did you see the printer tremble?"
                    print json_string
                    return render_template('success.html'), 200
            # TODO: now push it to the firs person in the matrix....
            else:
                #  We know that since this request was not initiated from a browser due to lack of session variable,
                #  it must have been initiated from the illumi books.
                # TODO: send out the image and audio links using websockets to next APPROPRIATE link in the matrix..
                username = request.form['username']
                if username == shuffled_list[-1]:
                    next_item = shuffled_list[-1]
                    web_socket = shared_module.connected_clients[next_item]
                    web_socket.send("7b484b06ede7409fae667cdf9fa24f5a.png")
                    # last item in list.. send images back to SERVER
                    return "Success mate!", 200
                elif username in shuffled_list[:-1]:
                    # all the other items in list..
                    # send it to the next person in the matrix..
                    item_position = shuffled_list.index(username)
                    next_item = shuffled_list[item_position+1]
                    web_socket = shared_module.connected_clients[next_item]
                    web_socket.send("http://jawrainey.me/img/me.jpg")
                    return render_template('success.html'), 200
            return redirect(url_for('track_whispers')), 200
    return render_template('userHome.html'), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/track')
def track_whispers():
    return render_template('track_whisper.html')