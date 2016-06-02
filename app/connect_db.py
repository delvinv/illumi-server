from flask import Flask
from flask.ext.mysql import MySQL
import config
import datetime
import MySQLdb
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

def get_id_from_project(username, title):
    query_a = "select project_id from BucketList.tbl_projects where title='{}' and user_username='{}'"
    query_b = query_a.format(title, username)
    cursor.execute(query_b)
    output = cursor.fetchone()
    print output[0]
    return output[0]


def add_new_whisper(username, title, current_timestamp):
    query = "INSERT INTO BucketList.tbl_projects(user_username, title, origin_date, status) VALUES('{}', '{}', '{}', 'started')"
    query_1 = query.format(username, title, current_timestamp)
    try:
        cursor.execute(query_1)
        conn.commit()
        print str(username) + " inserted successfully.."
        return get_id_from_project(username, title)
    except MySQLdb.IntegrityError, e:
        print "Not done " + str(e.args)
        conn.rollback()
        print e.message
        return None


# TODO: currently a copy of above method, make it more relevant..
def add_file_details_to_db(filename, project_id, media_type, username, current_timestamp):
    get_users_query = "INSERT INTO BucketList.tbl_media(filename, project_id, media_type, user_username, origin_date) VALUES('{}','{}','{}','{}', '{}') "
    final_query = get_users_query.format(filename, project_id, media_type, username, current_timestamp)

    try:
        cursor.execute(final_query)
        conn.commit()
        print str(username) + " inserted successfully.."
        return True
    except MySQLdb.IntegrityError, e:
        print "Not done " + str(e.args)
        conn.rollback()
        print e.message
        return False


def add_json_status_to_db(json_object, project_id):
    query = "UPDATE BucketList.tbl_projects SET status='{}' WHERE project_id='{}'"
    final_query = query.format(json_object, project_id)

    try:
        cursor.execute(final_query)
        conn.commit()
        print str(json_object) + " inserted successfully.."
        return True
    except MySQLdb.IntegrityError, e:
        print "Not done " + str(e.args)
        conn.rollback()
        print e.message
        return False


if __name__ == '__main__':
    current_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    # a = add_new_whisper("a@d", "my_diaries_7", current_timestamp)
    b = add_file_details_to_db("blah.mp3","19","audio","a@d",current_timestamp)
