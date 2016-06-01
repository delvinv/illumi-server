from flask import Flask

app = Flask(__name__)
from app import views
from app import whisper_views

from views_dir import user_management
# from whisper_views import *