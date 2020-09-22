from sqlite3 import connect, IntegrityError
from os import urandom


import src.globals
import src.crypto


def add_user(username, password, encryption_keys, signature_keys):

    db_connection = connect("./src/db")
    db_cursor = db_connection.cursor()

    username_insertion_query = """INSERT INTO USERS (username, salt, challenge, \
        solution, encryption_keys, signature_keys) VALUES (?, ?, ?, ?, ?, ?)"""

    salt = urandom(16)
    key = src.crypto.kdf(src.globals.HASH_SIZE, password, salt)

    solution = urandom(32)
    challenge = src.crypto.symmetrically_encrypt(solution, key)

    encryption_keys = src.crypto.symmetrically_encrypt(encryption_keys, key)
    signature_keys = src.crypto.symmetrically_encrypt(signature_keys, key)

    try:
        db_cursor.execute(username_insertion_query, (username, salt, challenge, \
            solution, encryption_keys, signature_keys))
    # VARIABLE TABLE NAMES AREN'T ALLOWED. I AM REALLY NOT LIKING THIS. NEED A WORKAROUND.
    # ASSUMING THE USER DOES NOT WANT TO PERFORM SQL INJECTIONS ON HIS OWN COMPUTER!
        table_creation_query = """CREATE TABLE """ + username + """ (id INTEGER PRIMARY KEY, message BLOB)"""
        db_cursor.execute(table_creation_query)

    except IntegrityError:
        print("Username already exists in DB!")
        return 1

    db_connection.commit()
    return 0
