# Mailing support imports
from flask import render_template
from app import app
from threading import Thread
from flask_mail import Mail, Message
from app import secret_config
# from flask.ext.mail import Mail, Message
app.config.from_object(secret_config)
mail = Mail(app)
from app.secret_config import *


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()


def whisper_finished_notification(whisper_id, email):
    # TODO: get whisper_name and User's full name based on info we have..
    # PLACEHOLDER..
    whisper_url = "http://illumi.delv.in/track"
    subject_string = "[illumi]Your whisper '{}' has returned!".format(whisper_id)
    send_email(subject_string,
               secret_config.MAIL_USERNAME,
               [email, 'd.varghese2@ncl.ac.uk'],
               render_template("whisper_completed_email.txt",
                               whisper_name=whisper_id,
                               whisper_url=whisper_url),
               render_template("whisper_completed.html",
                               whisper_name=whisper_id,
                               whisper_url=whisper_url))
    return "OK"