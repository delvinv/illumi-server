from flask import Flask
from flask.ext.mysql import MySQL
import config
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
from app import views

mysql = MySQL()

# Configurations
app.config['MYSQL_DATABASE_USER'] = config.my_username
app.config['MYSQL_DATABASE_PASSWORD'] = config.my_password
app.config['MYSQL_DATABASE_DB'] = config.my_db
app.config['MYSQL_DATABASE_HOST'] = config.my_host
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

_hashed_password = generate_password_hash(config.my_password)