from os.path import isfile, getsize, split

import src.utils
import src.crypto
import src.globals


# should this process go in sc.network?
def process(message, response_size)

    out, err = None, None

    message_id = src.utils.message_id()
    message["session_ID"] = src.globals.SESSION_ID
    message["message_id"] = message_id
	message["timestamp"] = src.utils.timestamp()
    message = src.utils.pack(message)

    request = src.crypto.symmetrically_encrypt(message, src.globals.KEY)
    del message
	request = src.utils.sizeof(request) + request

    err = src.network.send(request)
    if err:
        return (out, 1)

    response = src.network.recieve(response_size)
    if type(response) is int:
        return (out, 1)
    del request

    response = src.crypto.symmetrically_decrypt(response)
    if type(response) is int:
        return (out, 1)

    response = src.utils.unpack(response)
    if type(response) is not dict:
        return (out, 1)

    if response["message_id"] != message_id:
        print("message ID MISMATCH!")
        return (out, 1)

    # do look into rehashing speeds
    del response["message_id"]
    err = 0
    return response, 0


def download_public_keys(*IDs):

    out, err = None, None

    if not IDs:
        return (out, err)

    valid_IDs, invalid_IDs = [], []
	for ID in IDs:
        if src.utils.username_is_valid(ID):
            valid_IDs.append(ID)
        else:
            invalid_IDs.append(ID)

    if invalid_IDs:
        print("The following IDs are invalid:")
        [print(i) for i in invalid_IDs]

    if valid_IDs:
        print("Downloading Public keys...")
    else:
        return(out, err)

    response, err = process(
        {"request_code": src.globals.GET_PUBLIC_KEYS, "mail_id": valid_IDs}, \
            src.globals.BIG_RESPONSE)

    if err:
        return (None, 1)

    # process the response and insert the public keys
    # validate these keys before inserting them into
    # the keyring. Display a QR code-like graphical
    # representation also.

    """
    STRUCTURE OF THIS RESPONSE:
    request = {
        "username1": {
            "encryption_public_key": bytes,
            "signature_public_key": bytes}
        "username2": {
            "encryption_public_key": bytes,
            "signature_public_key": bytes}
        ...
            }
    """

    #VALIDATE RESPONSE HERE

    for username, keys in response.items():
        if src.crypto.key_is_valid(keys["encryption_public_key"]) and
            src.crypto.key_is_valid(keys["signature_public_key"]):

            if not src.crypto.key_exists_in_keyring(keys["encryption_public_key"]):
                out, err = src.crypto.insert_public_key(keys["encryption_public_key"])

            if not src.crypto.key_exists_in_keyring(keys["signature_public_key"]):
                out, err = src.crypto.insert_public_key(keys["signature_public_key"])

    out = None
    if err:
        err = 1
    else:
        err = 0

    return (out, err)


def refresh_mailbox():

	response = process(
        {"request_code": src.globals.UPDATE_MAILBOX}, src.globals.BIG_RESPONSE)

    if type(response) is int:
        print("FAILED to refresh mailbox!")
        return 1

    # sync mails with offline db here
    return 0


def delete_mail(from, *uid):

    """
    0 -> delete from the offline database
    1 -> delete from the server
    2 -> delete from both the server and the offline database
    """

    uid = list(uid)

	# DELETE MAIL FROM THE OFFLINE DB
	# OR DELETE MAIL FROM OFFLINE DB AND THEN SYNC THE DB
    if from:
    	response = process(
            {"request_code": src.globals.DELETE_EMAIL, "email_uid": uid}, src.globals.SMALL_RESPONSE)

        if type(response) is int:
            print("FAILED to delete mail!")
            return 1

    if from == 0 or from == 2:
        # delete stuff from the offline db


def send_mail(to, cc, bcc, subject, body, *attachments):

    """
    cc, bcc are lists of email addresses.
    subject, body are simple utf-8 strings.
    attachments must be file paths and NOT file objects.
    """

    mail =  { \

        "text": { \

            "content": { \

                "addresses": { \
                    "to": None, \
                    "cc": None, \
                    "bcc": None }, \

                "key": None,

                "text": { \
                    "subject": None, \
                    "body": None } \
                        }, \

            "signature": None}, \

        "attachments": { \

            "content" : {}, \

            "signature": None
                        } \
            }

    if attachments:
        size = 0
        attached = {}
        for attachment in attachments:
            if isfile(attachment):
                size += getsize(attachment)
                    if size > src.globals.MAX_MAIL_SIZE:
                        print("Maximum mail size limits exceeded!")
                        return 1
                fo = open(attachment, "rb")
                # split gives me the filename
                attached[split(attachment)[1]] = fo.read()
                fo.close()
            else:
                print(attachment, "NOT FOUND!")
                return 1
        attached = src.utils.pack(attached)
    else:
        del message["attachments"]

    # ASSERT SUBJECT LENGTH LIMITS (ONLY) WHEN SENDING MAILS
    # TO NON-DOMESTIC SERVERS BECAUSE OTHERWISE THEY'LL
    # GET TRUNCATED!

    text_content = { \
        "subject": subject, \
        "body": body}
    text_content = src.utils.pack(text_content)


    if len(cc) + len(bcc) + 1 > src.globals.MAX_RECIPIENTS:
        print("The maximum number of recipients you can add to an email is ", src.globals.MAX_RECIPIENTS)

    old_keys, new_keys = [], []
    if src.crypto.key_missing(to):
        new_keys.append(to)
    else:
        old_keys.append(to)
    for address in cc:
        if src.crypto.key_missing(address):
            new_keys.append(address)
        else:
            old_keys.append(address)
    for address in bcc:
        if src.crypto.key_missing(address):
            new_keys.append(address)
        else:
            old_keys.append(address)

    keys_found, keys_not_found = download_public_keys(new_keys)
    old_keys.append(keys_found)

    if keys_not_found:
        print("The following keys were NOT FOUND: ")
        for i in keys_not_found:
            print(i)

    if to not in old_keys:
        print("Reciepient Address NOT FOUND!")
        return 1

    request = {"request_code": src.globals.SEND_MAIL}

    # work with only those keys that have been found
    cc = list(set(cc) & set(old_keys))
    bcc = list(set(bcc) & set(old_keys))

    """
        key = src.crypto.symmetric_key_generator()

        encrypted_text_content = src.crypto.symmetrically_encrypt(text_content, key)
        text_content_signature = src.crypto.sign(src.crypto.hash(encrypted_text_content), )

        if attachments:
            encrypted_attachments = src.crypto.symmetrically_encrypt(attached, key)
            attachment_signature = src.crypto.sign(src.crypto.hash(encrypted_attachments, )
    """


def write_mail():

    to = input("To: ")
    cc = input("CC: ")
    bcc = input("BCC: ")

	return
