def add_user(username, password, encryption_keys, signature_keys):

    db_connection = db_connector("./libraries/db")
    db_cursor = db_connection.cursor()

    username_insertion_query = """INSERT INTO USERS (username, salt, challenge, \
        solution, encryption_keys, signature_keys) VALUES (?, ?, ?, ?, ?, ?)"""

    salt = urandom(16)
    print(type(password), type(salt))
    key = kdf(hash_size, password, salt)

    solution = urandom(32)
    challenge = symmetrically_encrypt(solution, key)

    encryption_keys = symmetrically_encrypt(encryption_keys, key)
    signature_keys = symmetrically_encrypt(signature_keys, key)

    db_cursor.execute(username_insertion_query, (username, salt, challenge, solution, \
        encryption_keys, signature_keys))
    db_connection.commit()
