from os.path import isfile

import src.utils
import src.crypto
import src.globals


def process(message, response_size)

    message_id = src.utils.message_id()
    message["message_id"] = message_id
	message["timestamp"] = src.utils.timestamp()
    message = src.utils.pack(message)

    request = src.crypto.symmetrically_encrypt(message, src.globals.KEY)
    del message
	request = src.utils.sizeof(request) + request

    err = src.network.send(request)
    if err:
        return 1

    response = src.network.recieve(response_size)
    if type(response) is int:
        return 1
    del request

    response = src.crypto.symmetrically_decrypt(response)
    if type(response) is int:
        return 1

    response = src.utils.unpack(response)
    if type(response) is not dict:
        return 1

    if response["message_id"] != message_id:
        print("message ID MISMATCH!")
        return 1

    # do look into rehashing speeds
    del response["message_id"]
    return response


def download_public_keys(*IDs):

    if not IDs:
        return 0

    valid_IDs, invalid_IDs = [], []
	for ID in IDs:
        if username_vailidity_checker(ID):
            invalid_IDs.append(ID)
        else:
            valid_IDs.append(ID)

    if invalid_IDs:
        print("The following IDs are invalid!")
        [print(i) for i in invalid_IDs]

    if valid_IDs:
        print("Downloading Public keys...")
    else:
        return (keys_found, keys_not_found)

    	response = process(
            {"request_code": src.globals.GET_PUBLIC_KEYS, "mail_id": valid_IDs}, src.globals.BIG_RESPONSE)

        # process the response and insert the public keys
        # validate these keys before inserting them into
        # the keyring. Display a QR code-like graphical
        # representation also.

        if type(response) is int:
            print("FAILED to download public keys!")
            return 1

        return (keys_found, keys_not_found)


def refresh_mailbox():

	response = process(
        {"request_code": src.globals.UPDATE_MAILBOX}, src.globals.BIG_RESPONSE)

    if type(response) is int:
        print("FAILED to refresh mailbox!")
        return 1

    # sync mails with offline db here
    return 0


def delete_mail(*uid):

    uid = list(uid)

	# DELETE MAIL FROM THE OFFLINE DB
	# OR DELETE MAIL FROM OFFLINE DB AND THEN SYNC THE DB

	response = process(
        {"request_code": src.globals.DELETE_EMAIL, "email_uid": uid}, src.globals.SMALL_RESPONSE)

    if type(response) is int:
        print("FAILED to delete mail!")
        return 1


def send_mail(to, cc, bcc, subject, body, *attachments):

    """
    cc, bcc are lists of email addresses.
    subject, body are simple utf-8 strings.
    attachments must be file paths and NOT file objects.
    """

    flag = False
    for file in attachments:
        if not isfile(file):
            print(file, " not found!")
            flag = True
    if flag:
        return 1

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

    print("")





	return


def write_mail():

	return
