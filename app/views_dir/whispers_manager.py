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

UPLOAD_FOLDER = 'uploads/'


@app.route('/startWhisper')
def startWhisper():
    if session.get('user'):
        return render_template('start_whisper.html')
    else:
        return render_template('error.html', error="Unauthorized access!")


# We need to find what devices are available and shuffle them each time a new whisper is started!
# Then it is stored in the database so that the whisper can be spread in the right order.
def shuffle_keys(whisper_id):
    #   time to shuffle and push to shared_module..
    keys_order = list(shared_module.connected_clients.keys())
    shuffle(keys_order)
    # shared_module.shuffled_keys = keys_order

    # Generate JSON of this shuffled order
    json_object = []
    for key in keys_order:
        inner_dict = {key:"False"}
        json_object.append(inner_dict)
    json_string = json.dumps(json_object)
    print "JSON IS: "+ json_string

    # post this shuffled order to the database...
    op_output = connect_db.add_json_status_to_db(json_string, whisper_id)
    print "DB operation for storing shuffle was: " + str(op_output)


@app.route('/uploadWhisper', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if file is present in the POST
        if 'file' not in request.files:
            print "No file part..."
            flash('No file part...')
            return redirect('/startWhisper')
        image_file = request.files['file']
        audio_file = request.files['audio_file']
        whisper_title = request.form['title']
        username = request.form['username']
        print str(audio_file)
        print "Files found for..."+str(username)
        # if user has not selected file, browser will also submit an empty part without filename.
        if image_file.filename == '' or audio_file.filename == '':
            print "No file selected bro....."
            flash('No selected file')
            return redirect(request.url)
        else:
            # Get the file extensions
            image_extension = os.path.splitext(image_file.filename)[1]
            audio_extension = os.path.splitext(audio_file.filename)[1]

            # Generate a uuid and save this image/audio as that name..
            gen_filename = uuid_generator.hex
            new_image = gen_filename + image_extension
            new_audio = gen_filename + audio_extension

            # Save the files to disk.
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_image))
            audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_audio))
            print "Files generated: " + str(new_audio) + ", " + str(new_image)

            current_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
            # username = session['user']
            whisper_id = connect_db.add_new_whisper(username, whisper_title, current_timestamp)
            audio_to_db = connect_db.add_file_details_to_db(new_audio,whisper_id,"audio",username,current_timestamp)
            image_to_db = connect_db.add_file_details_to_db(new_image,whisper_id,"image",username,current_timestamp)
            if audio_to_db:
                print "audio saved to database.."
            if image_to_db:
                print "image saved to database.."

            # if the form is posted from a browser, we can assume that it is a researcher sharing their content
            # and start the whisper process.
            if session['user']:
                shuffle_keys(whisper_id)

            return redirect(url_for('track_whispers'))
    return render_template('userHome.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/track')
def track_whispers():
    return render_template('track_whisper.html')