from db_config import config_connection
from mysql.connector import connect, Error

# connect to bd
def db_connect():
    try:
        with connect(**config_connection) as connection:
            print(connection)
    except Error as e:
        print(e)

# adding photo
def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def user_add_photo(filename, user_id):
    try:
        with connect(**config_connection) as connection:
            with connection.cursor() as cursor:
                blob_photo = convert_to_binary_data(filename)
                cursor.execute("""INSERT INTO 'users' 'photo' VALUES (%s) WHERE 'user_id' = (%s)""", blob_photo, user_id)
                connection.commit()
    except Error as e:
        print(e)

# getting photo
def write_file(binaryData, path):
    with open(path, 'wb') as file:
        file.write(binaryData)

def user_get_photo(path, user_id):
    try:
        with connect(**config_connection) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT * FROM 'users' WHERE 'user_id' = (%s)""", user_id)
                record = cursor.fetchall()
                for row in record:
                    image = row[2]
                    write_file(image, path)
    except Error as e:
        print(e)

# add user data

if (__name__ == '__main__'):
    db_connect()