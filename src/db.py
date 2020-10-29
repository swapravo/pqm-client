from sqlite3 import connect, IntegrityError
from os import urandom


import src.globals
import src.crypto


def backup_keys():
    if not src.globals.LOGGGED_IN or not src.globals.KEY:
        return 1

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()


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


    query = """UPDATE users SET pubkeys = ?, pubkeys_ = ?, secrets = ?, \
        secrets_ = ? WHERE username = ?"""

    try:
        db_cursor.execute(query, (pubkeys, pubkeys_, secrets, secrets_, src.globals.USERNAME))
        db_connection.commit()
    except:
        return 1
    return 0


def add_user(username, password):

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    username_insertion_query = """INSERT INTO USERS (username, salt, challenge, \
        solution, pubkeys, pubkeys_, secrets, secrets_) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

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
        db_cursor.execute(username_insertion_query, (username, salt, challenge, \
            solution, pubkeys, pubkeys_, secrets, secrets_))
        # VARIABLE TABLE NAMES AREN'T ALLOWED. I AM REALLY NOT LIKING THIS. NEED A WORKAROUND.
        # ASSUMING THE USER DOES NOT WANT TO PERFORM SQL INJECTIONS ON HIS OWN COMPUTER!
        table_creation_query = """CREATE TABLE """ + username + """ (id INTEGER \
            PRIMARY KEY, header BLOB, message BLOB)"""
        db_cursor.execute(table_creation_query)
        db_connection.commit()
    except IntegrityError:
        print("Username already exists in DB!")
        return 1
    return 0


def authenticate_user(username, password):
    password = bytes(password, 'utf-8')

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    query = """SELECT salt, challenge, solution FROM USERS WHERE username == ?"""
    db_cursor.execute(query, (username, ))
    try:
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

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    query = """SELECT * FROM SERVER_KEYS ORDER BY ID DESC LIMIT 1"""
    db_cursor.execute(query)
    data = db_cursor.fetchone()
    return data[1:]

"""
def fetch_mails(from, n):

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    while True:
        query = SELECT * FROM ? ORDER BY ID DESC LIMIT ?
        db_cursor.execute(query, (src.globals.USERNAME, n,))
    return
"""
