from flask import Flask
from flask.ext.mysql import MySQL
import config

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = config.my_username
app.config['MYSQL_DATABASE_PASSWORD'] = config.my_password
app.config['MYSQL_DATABASE_DB'] = config.my_db
app.config['MYSQL_DATABASE_HOST'] = config.my_host

mysql.init_app(app)
conn = mysql.connect()
conn.autocommit(True)

cursor = conn.cursor()
print "---Successfully connected to DB---"


def signup_to_database(username, email, password):
    insert_query = "INSERT INTO BucketList.tbl_user(user_name, user_username, user_password) VALUES('{}','{}','{}')"
    final_query = insert_query.format(username, email, password)
    print "Password is: " + password
    print "Query: " + final_query
    cursor.execute(final_query)
    output = cursor.fetchall()
    return output


def validate_email(email):
    get_users_query = "SELECT * FROM BucketList.tbl_user WHERE user_username='{}'"
    final_query = get_users_query.format(email)
    cursor.execute(final_query)
    output = cursor.fetchall()
    if len(output) > 0:
        print "SQL has output"
    print str(output)
    return output