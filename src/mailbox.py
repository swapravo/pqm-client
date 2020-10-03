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

    del response["message_id"]
    return response


def download_public_keys(*IDs):

	IDs = list(IDs)
	# validate IDs here

	response = process(
        {"request_code": src.globals.GET_PUBLIC_KEYS, "mail_id": IDs}, src.globals.BIG_RESPONSE)

    # process the response and insert the public keys

    if type(response) is int:
        print("FAILED to download public keys!")
        return 1

    return 0


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

    return 0


def send_mail(mail):

	return


def write_mail():

	return
