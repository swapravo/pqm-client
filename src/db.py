from sqlite3 import connect, IntegrityError
from os import urandom
from os.path import isfile, getsize


import src.globals
import src.crypto


db_connection = None
db_cursor = None


def backup_keys():
    if not src.globals.LOGGGED_IN or not src.globals.KEY:
        return 1

    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys", 'rb')
    pubkeys = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)
    fo.close()
    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys~", 'rb')
    pubkeys_ = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)
    fo.close()
    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets", 'rb')
    secrets = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)
    fo.close()
    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets~", 'rb')
    secrets_ = src.crypto.symmetrically_encrypt(fo.read(), src.globals.KEY)
    fo.close()

    query = """UPDATE keys SET pubkeys = ?, pubkeys_ = ?, secrets = ?, \
        secrets_ = ? WHERE username = ?"""

    try:
        db_cursor.execute(query, (pubkeys, pubkeys_, secrets, secrets_, src.globals.USERNAME))
        db_connection.commit()
    except:
        return 1
    return 0


def add_user(username, password):

    new_db_connection = connect("./src/databases/" + username)
    new_db_cursor = new_db_connection.cursor()

    key_table_query = """
        CREATE TABLE keys (
            username UNIQUE TEXT NOT NULL,
            salt UNIQUE BLOB NOT NULL,
            challenge UNIQUE BLOB NOT NULL,
            solution UNIQUE BLOB NOT NULL,
            pubkeys UNIQUE BLOB NOT NULL,
            pubkeys_ UNIQUE BLOB NOT NULL,
            secrets UNIQUE BLOB NOT NULL,
            secrets_ UNIQUE BLOB NOT NULL);
        """

    try:
        new_db_cursor.execute(key_table_query)
    except:
        return 1

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
    key = src.crypto.kdf(src.globals.HASH_SIZE, password, salt)
    solution = urandom(32)
    challenge = src.crypto.symmetrically_encrypt(solution, key)

    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys", 'rb')
    pubkeys = src.crypto.symmetrically_encrypt(fo.read(), key)
    fo.close()
    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"pubkeys~", 'rb')
    pubkeys_ = src.crypto.symmetrically_encrypt(fo.read(), key)
    fo.close()
    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets", 'rb')
    secrets = src.crypto.symmetrically_encrypt(fo.read(), key)
    fo.close()
    fo = open(src.globals.USER_HOME+src.globals.CCR_FOLDER+"secrets~", 'rb')
    secrets_ = src.crypto.symmetrically_encrypt(fo.read(), key)
    fo.close()

    try:
        new_db_cursor.execute(data_insertion_query, (username, salt, challenge, \
            solution, pubkeys, pubkeys_, secrets, secrets_))

        # VARIABLE TABLE NAMES AREN'T ALLOWED. I AM REALLY NOT LIKING THIS. NEED A WORKAROUND.
        # ASSUMING THE USER DOES NOT WANT TO PERFORM SQL INJECTIONS ON HIS OWN COMPUTER!
        message_table_query = """
            CREATE TABLE messages
                (id INTEGER,
                PRIMARY KEY,
                header BLOB NOT NULL,
                message BLOB NOT NULL)
            """

        new_db_cursor.execute(message_table_query)
        new_db_connection.commit()

    except:
        return 1
    return 0


def authenticate_user(username, password):

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
    except:
        return 1

    key = src.crypto.kdf(src.globals.HASH_SIZE, password, salt)

    if src.crypto.symmetrically_decrypt(challenge, key) == solution:
        print("User authenticated!")
        src.globals.KEY = key
        return 0
    print("User authentication FAILED!")
    return 1


def fetch_server_keys():

    db_connection = connect("./src/databases/server_keys")
    db_cursor = db_connection.cursor()

    query = """SELECT * FROM SERVER_KEYS ORDER BY ID DESC LIMIT 1"""
    db_cursor.execute(query)
    data = db_cursor.fetchone()
    return data[1:]


## BUG: NOT TESTED
def user_exists(username):
    if not src.utils.issqlite3("./src/databases/" + username):
        return False

    query = """
        SELECT username
        FROM keys
        WHERE username=?
        """

    db_cursor.execute(query, (username,))
    data = db_cursor.fetchone()
    if data:
        print(data)
        return True
    return False


def initialise_database(username):
    src.db.db_connection = connect("./src/databases/" + username)
    src.db.db_cursor = db_connection.cursor()


"""
def fetch_mails(from, n):

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    while True:
        query = SELECT * FROM ? ORDER BY ID DESC LIMIT ?
        db_cursor.execute(query, (src.globals.USERNAME, n,))
    return
"""
