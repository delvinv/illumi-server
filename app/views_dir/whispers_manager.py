import logging
logging.basicConfig(filename='logs/illumi_whispers.log',level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S')

from flask import Flask, render_template, request, json, redirect, session, url_for, flash
from app import app
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import datetime
from .. import connect_db
import shared_module
from random import shuffle
import email_sending

import uuid

WEB_URL = "http://52.40.252.108/"
INTERNAL_UPLOAD_FOLDER = 'app/static/uploads/'
PUBLIC_UPLOAD_FOLDER = 'uploads/'


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
    logging.info("JSON IS: "+ json_string)
    return json_string


def save_file_and_return_url(file_sent, file_suffix):
    # Get the file extensions
    file_extension = os.path.splitext(file_sent.filename)[1]
    final_file = WEB_URL + PUBLIC_UPLOAD_FOLDER + file_suffix + file_extension
    saving_file = INTERNAL_UPLOAD_FOLDER + file_suffix + file_extension

    # Save the files to disk.
    file_sent.save(os.path.join(saving_file))
    print "[STATUS] Files generated: " + str(final_file)
    logging.info("[STATUS] Files generated: " + str(final_file))
    return final_file


def generate_form_contents_json(audio_file, image_file, whisper_id):
    form_contents_json = {
        "audio_url":audio_file,
        "image_url":image_file,
        "whisper_id":whisper_id
    }
    form_contents_json_string = json.dumps(form_contents_json)
    return form_contents_json_string


@app.route('/mail')
def wow_mail():
    # a = send_email("Hello World",secret_config.MAIL_USERNAME,['delvin.friends@gmail.com'],"Why not email","<h1>Flask Email</h1>")
    a = email_sending.whisper_finished_notification("hohohoh")
    print a
    logging.info(a)
    return render_template('error.html' ,error="Email sent?")


def get_position_on_whisper_list(whisper_list, username):
    counter = 0
    for key in whisper_list:
        if username in key:
            return counter
        counter += 1


def handle_researcher_upload(username, image_file, audio_file):
    print "[STATUS] User is logged in..."
    logging.info("[STATUS] User is logged in...")
    current_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    # Set the whisper_id by adding it to the database and retrieving a unique id..
    whisper_title = request.form['whisper_title']
    user_email = session['user_email']
    whisper_id = connect_db.add_new_whisper(user_email, whisper_title, current_timestamp)

    # Generate a uuid that will be used to name files before saving them..
    gen_filename = uuid.uuid4().hex
    # Based on this filename, we can save files to disk..
    form_image_url = save_file_and_return_url(image_file, gen_filename)
    form_audio_url = save_file_and_return_url(audio_file, gen_filename)
    # Now we save file information to the media database (SQL)
    connect_db.add_file_details_to_db(form_audio_url,whisper_id,"audio",username,current_timestamp)
    connect_db.add_file_details_to_db(form_image_url,whisper_id,"image",username,current_timestamp)
    # Generate a JSON object that will be sent to Pi devices..
    form_contents_json_string = generate_form_contents_json(form_audio_url, form_image_url, whisper_id)

    shuffled_list = create_shuffled_list(whisper_id)
    if shuffled_list is not None:
        keys_json_string = convert_keys_to_json(shuffled_list)
        # post this shuffled order to the database...
        op_output = connect_db.add_json_status_to_db(keys_json_string, whisper_id)
        print "DB operation for storing shuffle was: " + str(op_output)
        logging.info("DB operation for storing shuffle was: " + str(op_output))

        next_item = shuffled_list[0]
        try:
            web_socket = shared_module.connected_clients[next_item]
            web_socket.send(form_contents_json_string)
        except Exception, e:
            print "[WHISPERS] Socket broke when researcher uploaded.."
            logging.info("[WHISPERS] Socket broke when researcher uploaded..")
        print "Did you see the printer tremble?"
        print form_contents_json_string
        logging.info("Did you see the printer tremble?")
        logging.info(form_contents_json_string)
        return True


def forwarding_whisper_next_client(existing_whisper_list, form_contents_json_string, username, whisper_id):
    print "[PI] " + "We have a long way to go.."
    logging.info("[PI] " + "We have a long way to go..")

    # Get current position of username in the list
    current_position = get_position_on_whisper_list(existing_whisper_list, username)

    # Based on this position, increment it, and get the next item...
    next_item = existing_whisper_list[current_position+1]
    print "[PI] " + "next_item: " + str(next_item.keys()[0])
    logging.info("[PI] " + "next_item: " + str(next_item.keys()[0]))
    next_item_name = str(next_item.keys()[0])
    existing_whisper_list[current_position][username] = "has_sent"
    whisper_list_stringified = json.dumps(existing_whisper_list)
    connect_db.add_json_status_to_db(whisper_list_stringified, whisper_id)
    print "[PI] Connected Sockets: " + str(shared_module.connected_clients.keys())
    logging.info("[PI] Connected Sockets: " + str(shared_module.connected_clients.keys()))
    try:
        web_socket = shared_module.connected_clients[next_item_name]
        if not web_socket.closed:
            web_socket.send(form_contents_json_string)
            print "[PI] Success sending to " + next_item_name
            logging.info("[PI] Success sending to " + next_item_name)
        else:
            print "[PI] Failed sending to " + next_item_name
            logging.info("[PI] Failed sending to " + next_item_name)
            new_next_item = existing_whisper_list[current_position+2].keys()[0]
            print "Retrying with next PI on list.. " + str(new_next_item)
            logging.info("Retrying with next PI on list.. " + str(new_next_item))

            web_socket_2 = shared_module.connected_clients[new_next_item]
            web_socket_2.send(form_contents_json_string)

            print "[PI] Re-success sending to " + str(new_next_item)

        existing_whisper_list[current_position+1][next_item_name] = "has_received"
        existing_whisper_list_string = json.dumps(existing_whisper_list)
        connect_db.add_json_status_to_db(existing_whisper_list_string, whisper_id)
        #
        # Changing the status of the Pi that has just sent us..
        return True
    except KeyError, k:
        print "[DB] " + "Websocket KeyError: No socket with name " + next_item_name + " exists."
        logging.info("[DB] " + "Websocket KeyError: No socket with name " + next_item_name + " exists.")
        existing_whisper_list[current_position+1][next_item_name] = "failed_receive"
        existing_whisper_list_string = json.dumps(existing_whisper_list)
        connect_db.add_json_status_to_db(existing_whisper_list_string, whisper_id)
        return False


def forward_final_whisper_to_researcher(existing_whisper_list, username, whisper_id):
    print "[PI] " + "Final PI"
    logging.info("[PI] " + "Final PI")
    # last item in list.. send images back to SERVER
    existing_whisper_list[-1][username] = "has_sent"
    whisper_list_string = json.dumps(existing_whisper_list)
    updating_code = connect_db.add_json_status_to_db(whisper_list_string, whisper_id)
    print "[PI] " + "DEFCON updating code: " + str(updating_code)
    logging.info("[PI] " + "DEFCON updating code: " + str(updating_code))
    # Send an email to the researcher that their file is back!
    _email = connect_db.get_username_from_whisper_id(whisper_id)
    print "[EMAIL] about to send to " + str(_email)
    logging.info("[EMAIL] about to send to " + str(_email))
    email_sending.whisper_finished_notification(whisper_id, _email)
    return True


@app.route('/upload', methods=['POST', 'GET'])
@app.route('/uploadWhisper', methods=['POST', 'GET'])
def upload_whisper_form():
    print "[PI] Connected Sockets: " + str(shared_module.connected_clients.keys())
    logging.info("[PI] Connected Sockets: " + str(shared_module.connected_clients.keys()))
    print "[" + request.method + "] Request.. "
    logging.info("[" + request.method + "] Request.. ")
    if request.method == 'POST':
        # check if File is present in the POST
        if 'audio_file' not in request.files:
            print "No file part..."
            logging.info("[WHISPERS] No file part...")
            return redirect('/startWhisper'), 400
        else:
            print "[STATUS] Valid file "
        image_file = request.files['image_file']
        print "[STATUS] Valid image file "
        logging.info("[STATUS] Valid image file ")
        audio_file = request.files['audio_file']
        print "[STATUS] Valid audio "
        logging.info("[STATUS] Valid audio ")
        username = request.form['username']
        print "[STATUS] Valid username"
        logging.info("[STATUS] Valid username")
        # if user has not selected file, browser will also submit an empty part without filename.
        if image_file.filename == '' or audio_file.filename == '':
            print "No file selected bro....."
            logging.error("No file selected.....")
            flash('No selected file')
            return redirect(request.url), 400

        current_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        # if the form is posted from a browser, we can assume that it is a researcher sharing their content
        # and start the whisper process.
        # check if username is a researcher or participant...
        if 'user' in session:
            op_output_success = handle_researcher_upload(username, image_file, audio_file)
            if op_output_success:
                return render_template('error.html', error="Successfully started whisper. You will receive an email when completed."), 200
            else:
                return render_template('error.html', error="Unfortunately, an error occurred. Sorry not feeling helpful right now."), 400
        else:
            # Request is from a Pi so we need to get the whisper_id for which the Pi has sent a request to the server..
            whisper_id = request.form['whisper_id']
            print "[PI] " + "Received request from whisper: " + str(whisper_id)
            logging.info("[PI] " + "Received request from whisper: " + str(whisper_id))
            whisper_list = connect_db.get_json_status_from_db(whisper_id)
            print "[PI] " + str(whisper_list) + ", type: " + str(type(whisper_list))
            logging.info("[PI] " + str(whisper_list) + ", type: " + str(type(whisper_list)))
            existing_whisper_list = json.loads(str(whisper_list))
            print "[PI] " + str(existing_whisper_list)  + ", type: " + str(type(existing_whisper_list))
            logging.info("[PI] " + str(existing_whisper_list)  + ", type: " + str(type(existing_whisper_list)))

            # if this Pi has already sent us files for this whisper, we can stop further processing..
            # Check if a) user is a valid one, b) user hasnt already sent us a file!
            bool_pi_found_in_list = False
            for item in existing_whisper_list:
                if username in item:
                    bool_pi_found_in_list = True
                    if item[username]== "has_sent":
                        print "[PI] " + "This Pi has already sent us files.."
                        logging.info("[PI] " + "This Pi has already sent us files..")
                        return "Already received files from this Pi", 400
                    else:
                        print "[PI] " + "Fresh files. Not previously received from " + str(item)
                        logging.info("[PI] " + "Fresh files. Not previously received from " + str(item))
            if not bool_pi_found_in_list:
                print "[PI] " + "Naughty Pi! Not meant to be sending us files!"
                logging.info("[PI] " + "Naughty Pi! Not meant to be sending us files!")
                return "Pi is not on list whisper receivers.", 400

            # Generate a filename, and then save the audio. image files in database and then on disk..
            gen_filename = uuid.uuid4().hex
            form_image_url = save_file_and_return_url(image_file, gen_filename)
            form_audio_url = save_file_and_return_url(audio_file, gen_filename)
            form_contents_json_string = generate_form_contents_json(form_audio_url, form_image_url, whisper_id)

            connect_db.add_file_details_to_db(form_audio_url,whisper_id,"audio",username,current_timestamp)
            connect_db.add_file_details_to_db(form_image_url,whisper_id,"image",username,current_timestamp)
            print "[PI] " + "Files saved to DB and disk e.g. ("+str(form_image_url) + ")"
            logging.info("[PI] " + "Files saved to DB and disk e.g. ("+str(form_image_url) + ")")


            # parse the status, get the next one, get the last one, and send it to the next one..
            #  We know that since this request was not initiated from a browser due to lack of session variable,
            #  it must have been initiated from the illumi books.
            # TODO: send out the image and audio links using websockets to next APPROPRIATE link in the matrix..

            if username in existing_whisper_list[-1]:
                success_boolean = forward_final_whisper_to_researcher(existing_whisper_list, username, whisper_id)
                if success_boolean:
                    return "Final Pi has uploaded..!", 200
                else:
                    return "Final PI failed to fully upload", 400
            else:
                success_boolean = forwarding_whisper_next_client(existing_whisper_list, form_contents_json_string, username, whisper_id)
                if success_boolean:
                    return "Received from PI gratefully, now next PI..", 200
                else:
                    return "Could not forward to next PI. Aw shucks :(", 400
        return redirect(url_for('track_whispers')), 200
    return render_template('about.html'), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


# This is where researchers can track their whispers...
@app.route('/trackWhisper')
@app.route('/track')
def track_whispers():
    if not session.get('user'):
        return render_template('error.html', error="Unauthorized access!")
    if session.get('user_email'):
        user_name = session['user_email']
        # Check what whispers exist from that author and create links for them..
        media_collection = connect_db.get_media_for_username(user_name)

        audio_filenames_list = []
        image_filenames_list = []
        whisper_names_list = []
        for item in media_collection:
            try:
                print item
                print "ITEM IS: " + str(item["audio_filenames"][0][0])
                logging.info("ITEM IS: " + str(item["audio_filenames"][0][0]))
                audio_filenames_list.append(str(item["audio_filenames"][0][0]))
                image_filenames_list.append(str(item["image_filenames"][0][0]))
                whisper_names_list.append(str(item["whisper_names"][0][0]))
            except Exception, e:
                print "[WHISPERS] Exception.. \n" + str(e.message)
        # Generate all the whispers and links on a single page..
        print audio_filenames_list
        logging.info(audio_filenames_list)
        return render_template('track_whisper.html',
                               audio_filenames_list=audio_filenames_list,
                               whisper_names_list=whisper_names_list,
                               image_filenames_list=image_filenames_list)
    else:
        return render_template('error.html', error="Unauthorized access!")


# Backup method if websockets doesnt work for server to pi connection..
@app.route('/check_whispers')
def check_whispers():
    if request.method=='POST':
        print "TBC"
        # Check if there are whispers waiting that need this Pi as the next receiver..
        # Put the first match whisper image and audio into a json
        # Convert json into strings..
        # Send json as a response using make_response and return it here..
    else:
        return render_template("error.html")
