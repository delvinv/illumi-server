from flask import Flask

app = Flask(__name__)
from app import views
from app import whisper_views

from views_dir import user_management
from views_dir import whispers_manager
from views_dir import sockets_manager
# from whisper_views import *