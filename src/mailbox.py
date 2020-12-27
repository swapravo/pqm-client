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

    response, err = src.crypto.symmetrically_decrypt(response)
    if err:
        return (None, 1)

    response = src.utils.unpack(response)
    if type(response) is not dict:
        return (None, 1)

    if response["message_id"] != message_id:
        print("message ID MISMATCH!")
        return (None, 1)

    # do look into rehashing speeds
    del response["message_id"]
    err = 0
    return (response, 0)


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

    response, err = src.mailbox.process(
        {"request_code": src.globals.GET_PUBLIC_KEYS, "mail_id": valid_IDs}, \
            src.globals.BIG_RESPONSE)

    if err:
        return (None, 1)

    # process the response and INSERT THE PUBLIC KEYS
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
    # print it out if the public key corresponding
    # to an username is not found!

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
    # this only downlads the metadata about the emails
    # if you want a certain mail, you download_mail() with the idea
    # of the emails

    out, err = src.mailbox.process(
        {"request_code": src.globals.UPDATE_MAILBOX}, src.globals.BIG_RESPONSE)

    if err:
        print("Failed to refresh mailbox! Error:", err)
        return (None, 1)

    if out == src.globals.NO_CHANGES_IN_MAILBOX:
        print("No changes in mailbox!")
        return (None, 0)
    else:
        # parse email metadata here and insert it into the db
        # update the current view?
        pass


def delete_mail(from, *uid):

    """
    0 -> delete from the offline database
    1 -> delete from the server
    2 -> delete from both the server and the offline database
    """

    uid = list(uid)

	# DELETE MAIL FROM THE OFFLINE DB
	# OR DELETE MAIL FROM OFFLINE DB AND THEN SYNC THE DB
    # DECIDE ON HOW THE EMAILS WILL BE INDEXED AND UNIQUELY IDENTIFIED

    if from:
    	response, err = process(
            {"request_code": src.globals.DELETE_EMAIL, "email_uid": uid}, src.globals.SMALL_RESPONSE)

        if err:
            print("FAILED to delete mail!")
            return (None, 1)

    if from == 0 or from == 2:
        # delete stuff from the offline db
        for each_uid in uid:
            out, err = src.db.delete_mail(each_uid)
            if err:
                print("Failed to delete mail", each_uid, "!\n\tError:", err)


def send_mail(to, cc, bcc, subject, body, *attachments):

    """
    cc, bcc are lists of email addresses.
    subject, body are simple utf-8 strings.
    attachments must be file paths and NOT file objects.

    if we have fields for addresses "inside" the email, the
    server wont be able to read them...
    if we send a copy of the addresses along with the email,
    someone will tweak the source
    to fuck with the list of recipients.
    Breaking up the email into multiple parts: addresses, text content, attachments
    will unnecessariliy complicate stuff.
    What the server can do is ask the user to sign the
    addresses that it says it wants to send the mails to,
    in addition to the emails, which already have all the necessary fields:
    addresses, text, attachments.
    """

    if len(cc) + len(bcc) + 1 > src.globals.MAX_RECIPIENTS:
        print("The maximum number of recipients you can add to an email is ", \
        src.globals.MAX_RECIPIENTS)
        return (None, 1)

    if attachments:
        size = 0
        media = {}
        for attachment in attachments:
            if isfile(attachment):
                size += getsize(attachment)
                    if size > src.globals.MAX_MAIL_SIZE:
                        print("Maximum mail size limits exceeded!")
                        return (None, 1)
                fo = open(attachment, "rb")
                # split gives me the filename
                media[split(attachment)[1]] = fo.read()
                fo.close()
            else:
                print(attachment, "NOT FOUND!")
                return (None, 1)

    # ASSERT SUBJECT LENGTH LIMITS (? / ONLY) WHEN SENDING MAILS
    # TO NON-DOMESTIC SERVERS BECAUSE OTHERWISE THEY'LL
    # GET TRUNCATED!

    recipients = [to] + cc + bcc
    new_keys = []

    for recipient in recipients:
        if not src.crypto.key_exists_in_keyring(recipient):
            new_keys.append(recipient)

    if new_keys:
        out, err = src.mailbox.download_public_keys(new_keys)
        if err:
            return (None, 1)

    # tell the server that we'll be sending quite a lot of data!
    # request = {"request_code": src.globals.SEND_MAIL}
    # please fix the cc bcc issue. i am really sick of it

    mail = src.utils.pack({
        "timestamp": src.utils.timestamp(),
        "text": {
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "subject": subject,
            "body": body,
        "attachments": media
            }})

    envelope = {
        "signed_mail": {
            "signature": None,
            "mail": None,
            "key": None},
        "recipient": None}

    # i am assuming that i am working with a mail that just needs to be
    # encrypted and sent over to the sever
    # hash of the mail will be calculated on the plaintext

    mail_hash = src.crypto.hash(mail)

    for recipient in recipients:
        if src.crypto.key_exists_in_keyring(recipient):
            key = src.crypto.symmetric_key_generator()
            encrypted_mail = src.crypto.symmetrically_encrypt(mail, key)
            signature = src.crypto.sign(mail_hash, recipient)
            # asymmetrically_encrypt the key now and add it to the message
            key = src.crypto.asymmetrically_encrypt( \
                key, src.crypto.encryption_key(recipient))
            envelope["signed_mail"]["signature"] = signature
            envelope["signed_mail"]["mail"] = encrypted_mail
            envelope["signed_mail"]["key"] = key
            envelope["recipient"] = recipient

        src.network.process({'request_code': src.globals.SEND_MAIL, \
            'request': envelope}, src.globals.SMALL_RESPONSE)

def write_mail():

    to = src.utils.writer().split()
    cc = src.utils.writer().split()
    bcc = src.utils.writer().split()

    content = src.utils.writer()

    # do something that helps the user to attach media
    # parse the whole thing into a "mail object"

	return


def print_mailbox():
    # print the different FOLDERS in inbox
    pass


def process_mail(signed_mail):

    """
    emails downladed straight from the server (the envelope) need to
    be processed before they're inserted into the user's database
    """

    # perform data validations both on the server and the recipient's device

    key = src.crypto.asymmetrically_decrypt(signed_mail["key"], \
        src.crypto.encryption_key(src.globals.USERNAME))
    if key is None:
        return (None, 1)

    mail = src.crypto.symmetrically_decrypt(signed_mail["mail"], key)
    if mail is None:
        return (None, 1)

    hash, err = src.crypto.verify_signature(signed_mail["signature"])
    if err:
        return (None, 1)

    if hash != src.crypto.hash(mail):
        print("Hash verification of email FAILED!")
        return (None, 1)

    # now that the mail has been processed, insert it into the db

    return (None, 0)
