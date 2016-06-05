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
print "[DB] " + "---Successfully connected to DB---"


def signup_to_database(username, email, password):
    insert_query = "INSERT INTO BucketList.tbl_user(user_name, user_username, user_password) VALUES('{}','{}','{}')"
    final_query = insert_query.format(username, email, password)
    print "[DB] " + "Password is: " + password
    print "[DB] " + "Query: " + final_query
    cursor.execute(final_query)
    output = cursor.fetchall()
    return output


def validate_email(email):
    get_users_query = "SELECT * FROM BucketList.tbl_user WHERE user_username='{}'"
    final_query = get_users_query.format(email)
    cursor.execute(final_query)
    output = cursor.fetchall()
    if len(output) > 0:
        print "[DB] " + "Login SQL has output"
    print "[DB] " + str(output)
    return output


def get_username_from_project_id(project_id):
    get_users_query = "SELECT user_username FROM BucketList.tbl_projects WHERE project_id='{}'"
    final_query = get_users_query.format(project_id)
    cursor.execute(final_query)
    output = cursor.fetchone()
    if len(output) > 0:
        return output[0]
    return None


def get_id_from_project(username, title):
    query_a = "select project_id from BucketList.tbl_projects where title='{}' and user_username='{}'"
    query_b = query_a.format(title, username)
    cursor.execute(query_b)
    output = cursor.fetchone()
    print "[DB] " + str(output[0])
    return output[0]


def add_new_whisper(username, title, current_timestamp):
    query = "INSERT INTO BucketList.tbl_projects(user_username, title, origin_date, status) VALUES('{}', '{}', '{}', 'inactive')"
    query_1 = query.format(username, title, current_timestamp)
    try:
        cursor.execute(query_1)
        conn.commit()
        print "[DB] " + str(username) + " inserted successfully.."
        return get_id_from_project(username, title)
    except MySQLdb.IntegrityError, e:
        print "[DB] " + "Not done " + str(e.args)
        conn.rollback()
        print "[DB] " + e.message
        return None


# TODO: currently a copy of above method, make it more relevant..
def add_file_details_to_db(filename, project_id, media_type, username, current_timestamp):
    get_users_query = "INSERT INTO BucketList.tbl_media(filename, project_id, media_type, user_username, origin_date) VALUES('{}','{}','{}','{}', '{}') "
    final_query = get_users_query.format(filename, project_id, media_type, username, current_timestamp)

    try:
        cursor.execute(final_query)
        conn.commit()
        print "[DB] " + str(username) + " inserted successfully.."
        return True
    except MySQLdb.IntegrityError, e:
        print "Not done " + str(e.args)
        conn.rollback()
        print "[DB] " + e.message
        return False


def add_json_status_to_db(json_object, project_id):
    query = "UPDATE BucketList.tbl_projects SET status='{}' WHERE project_id='{}'"
    final_query = query.format(json_object, project_id)

    try:
        cursor.execute(final_query)
        conn.commit()
        print "[DB] " + str(json_object) + " inserted successfully.."
        return True
    except MySQLdb.IntegrityError, e:
        print "[DB] " + "Not done " + str(e.args)
        conn.rollback()
        print e.message
        return False


def get_json_status_from_db(project_id):
    query = "SELECT status FROM BucketList.tbl_projects WHERE project_id= '{}'"
    final_query = query.format(project_id)
    try:
        cursor.execute(final_query)
        conn.commit()
        output = cursor.fetchone()
        print "[DB] " + str(project_id) + " retrieved successfully.."
        return output[0]
    except MySQLdb.IntegrityError, e:
        print "[DB] " + "Not retrieved " + str(e.args)
        conn.rollback()
        print e.message
        return None



def get_media_from_db(project_id, media_type):
    query = "SELECT filename FROM BucketList.tbl_media WHERE project_id= '{}' AND media_type='{}' ORDER BY media_type ASC, origin_date ASC"
    final_query = query.format(project_id, media_type)
    try:
        cursor.execute(final_query)
        conn.commit()
        output = cursor.fetchall()
        print "[DB] " + str(project_id) + " retrieved successfully.."
        return output
    except MySQLdb.IntegrityError, e:
        print "[DB] " + "Not retrieved.. " + str(e.args)
        conn.rollback()
        print e.message
        return None


def get_projects_from_db(user_username):
    query = "SELECT * FROM BucketList.tbl_projects WHERE user_username= '{}'"
    final_query = query.format(user_username)
    try:
        cursor.execute(final_query)
        conn.commit()
        output = cursor.fetchall()
        print "[DB] " + str(user_username) + " retrieved successfully.."
        return output
    except MySQLdb.IntegrityError, e:
        print "[DB] " + "Not retrieved.. " + str(e.args)
        conn.rollback()
        print e.message
        return None


def get_media_for_username(username):
    try:
        projects_list = get_projects_from_db(username)
        project_media = []
        for project in projects_list:
            project_id = project[0]
            project_name = project[2]

            audio_filenames = get_media_from_db(project_id, "audio")
            image_filenames = get_media_from_db(project_id, "image")

            project_single = {"project_name": project_name, "audio_filenames": audio_filenames, "image_filenames": image_filenames}
            project_media.append(project_single)
    except Exception, e:
        print "[DB] error " +e.message
    return project_media

if __name__ == '__main__':
    current_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    # a = add_new_whisper("a@d", "my_diaries_7", current_timestamp)
    b = add_file_details_to_db("blah.mp3","19","audio","a@d",current_timestamp)
