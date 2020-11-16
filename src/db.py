from sqlite3 import connect, IntegrityError
from os import urandom
from os.path import isfile, getsize

import src.globals
import src.crypto


db_connection = None
db_cursor = None


def backup_keys():

    """
    Encrypts the keyring and stores it in the user's database.
    """

    out, err = None, 1

    if not src.globals.LOGGGED_IN or not src.globals.KEY:
        print("Please login first!")
        return (out, err)

    try:
        with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys", 'rb') as fo:
            pubkeys = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)

        with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys~", 'rb') as fo:
            pubkeys_ = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)

        with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets", 'rb') as fo:
            secrets = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)

        with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets~", 'rb') as fo:
            secrets_ = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)

    except Error as e:
        print("File error:", e)
        return (out, err)

    query = """
        UPDATE keys
            SET pubkeys = ?,
                pubkeys_ = ?,
                secrets = ?,
                secrets_ = ?
            WHERE username = ?
            """

    try:
        db_cursor.execute(query, \
            (pubkeys, pubkeys_, secrets, secrets_, src.globals.USERNAME))
        db_connection.commit()
    except Error as e:
        print("Database Error:", e)
        return (out, err)

    err = 0
    return (out, err)


def add_user(username, password):

    """
    Create a new database for every new user.
    Make two tables: one to store the keys, and
    one to stores messages.
    """

    out, err = None, 1

    key_table_query = """
        CREATE TABLE keys (
            username TEXT UNIQUE NOT NULL,
            salt BLOB UNIQUE NOT NULL,
            challenge BLOB UNIQUE NOT NULL,
            solution BLOB UNIQUE NOT NULL,
            pubkeys BLOB UNIQUE NOT NULL,
            pubkeys_ BLOB UNIQUE NOT NULL,
            secrets BLOB UNIQUE NOT NULL,
            secrets_ BLOB UNIQUE NOT NULL)
        """

    try:
        new_db_connection = connect("./src/databases/" + username)
        new_db_cursor = new_db_connection.cursor()
        new_db_cursor.execute(key_table_query)

    except Exception as e:
        print("Database error:", e)
        return (out, err)

    data_insertion_query = """
        INSERT INTO keys (
            username,
            salt,
            challenge,
            solution,
            pubkeys,
            pubkeys_,
            secrets,
            secrets_)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """

    salt = urandom(16)
    solution = urandom(32)

    key = src.crypto.kdf(src.globals.HASH_SIZE, password, salt)
    challenge = src.crypto.symmetrically_encrypt(solution, key)

    with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys", 'rb') as fo:
        pubkeys = src.crypto.symmetrically_encrypt(fo.read(), key)

    with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys~", 'rb') as fo:
        pubkeys_ = src.crypto.symmetrically_encrypt(fo.read(), key)

    with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets", 'rb') as fo:
        secrets = src.crypto.symmetrically_encrypt(fo.read(), key)

    with open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets~", 'rb') as fo:
        secrets_ = src.crypto.symmetrically_encrypt(fo.read(), key)

    message_table_query = """
        CREATE TABLE messages
            (id INTEGER PRIMARY KEY,
            header BLOB NOT NULL,
            message BLOB NOT NULL)
        """

    try:
        new_db_cursor.execute(data_insertion_query, (username, salt, challenge, \
            solution, pubkeys, pubkeys_, secrets, secrets_))
        new_db_cursor.execute(message_table_query)
        new_db_connection.commit()

    except Exception as e:
        print("Database Error:", e)
        return (out, err)

    out, err = initialise_database(username)
    if err:
        print("Failed to initialise database!")
        return (out, err)

    err = 0
    print("Added user successfully!")
    return (out, err)


def authenticate_user(username, password):

    out, err = None, 1

    if not isinstance(password, bytes):
        password = bytes(password, 'utf-8')

    query = """
        SELECT salt, challenge, solution
        FROM keys
        WHERE username == ?
        """

    try:
        db_cursor.execute(query, (username,))
        salt, challenge, solution = db_cursor.fetchone()

    except Error as e:
        print("Database error:", e)
        return (out, err)

    key = src.crypto.kdf(src.globals.HASH_SIZE, password, salt)

    err = 0
    if src.crypto.symmetrically_decrypt(challenge, key) == solution:
        print("User authenticated!")
        src.globals.KEY = key
        out = True
    else:
        print("User authentication FAILED!")
        out = False

    return (out, err)


def fetch_server_keys():

    out, err = None, 1

    try:
        db_connection = connect("./src/databases/server_keys")
        db_cursor = db_connection.cursor()

        query = """
            SELECT * FROM SERVER_KEYS
            ORDER BY ID DESC
            LIMIT 1
            """
        db_cursor.execute(query)
        data = db_cursor.fetchone()
        out = data[1:]

    except Error as e:
        print("Database Error:", e)
        err = 1
    err = 0
    return (out, err)


def initialise_database(username):

    out, err = None, 1

    try:
        src.db.db_connection = connect("./src/databases/" + username)
        src.db.db_cursor = db_connection.cursor()
    except Exception as e:
        print("Failed to initialise database: ", e)
    err = 0
    return (out, err)


"""
def fetch_mails(from, n):

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    while True:
        query = SELECT * FROM ? ORDER BY ID DESC LIMIT ?
        db_cursor.execute(query, (src.globals.USERNAME, n,))
    return
"""
