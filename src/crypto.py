from os import urandom
from os.path import isfile
from sys import byteorder
from hashlib import blake2b
from nacl.pwhash.argon2id import kdf
from nacl.secret import SecretBox #xsalsa20poly1305
from nacl.utils import random as nonce_generator


import src.globals
import src.utils


def encryption_key(username):
	return username + ".qmek"


def signature_key(username):
	return username + ".qmsk"


def hash(message):
	return blake2b(message, digest_size=src.globals.HASH_SIZE).digest()


def insert_public_key(key, keyname):
	out, err = src.utils.execute("./src/ccr -y -i --name " + keyname, key)
	if err or out:
		return 1
	return 0


def insert_private_key(key, keyname):
	out, err = src.utils.execute("./src/ccr -y -I --name " + keyname, key)
	if err or out:
		return 1
	return 0


def remove_public_key(keyname):
	out, err = src.utils.execute("./src/ccr -y -x " + keyname)
	if err or out:
		return 1
	return 0


def remove_private_key(keyname):
	out, err = src.utils.execute("./src/ccr -y -X " + keyname)
	if err or out:
		return 1
	return 0


def generate_encryption_keys(keyname):
	print("Generating asymmetric encryption keys.")
	print("THESE FILES NEED TO BE (f)LOCKED!!!")
	out, err = src.utils.execute("./src/ccr --gen-key ENC-256 --name " + keyname)
	if not bytes("Gathering random seed bits from kernel", 'utf-8') in err:
		print(err)
		return 1
	return keyname


def generate_signature_keys(keyname):
	print("Generating signing Keys. This is going to take a while.")
	print("THESE FILES NEED TO BE (f)LOCKED!!!")
	out, err = src.utils.execute("./src/ccr --gen-key SIG-256 --name " + keyname)
	if not bytes("Gathering random seed bits from kernel", 'utf-8') in err:
		print(err)
		return 1
	return keyname


def key_fingerprint(keyname):

	if keyname[-2] == 'p':
		mode = 'k'
	elif keyname[-2] == 's':
		mode = 'K'
	else:
		return 1

	out, err = src.utils.execute("./src/ccr -" + mode + " --fingerprint -F " + keyname)
	if err: return 1
	return bytes.fromhex(''.join(str(out[-81:-2], 'utf-8').split(':')))


def asymmetrically_encrypt(message, public_key_name):

	out, err = src.utils.execute("./src/ccr -e -r " + public_key_name, message)

	if not out or err: return 1
	return out


def asymmetrically_decrypt(message, private_key_name):

	out, err = src.utils.execute("./src/ccr -d -r " + private_key_name, message)

	if not out or err: return 1
	return out


def sign(message, recipient_name):

	out, err = src.utils.execute("./src/ccr -s -r " + recipient_name, message)

	if err: return 1
	return out


def verify_signature(signature):
	out, err = src.utils.execute("./src/ccr -v ", signature)

	# i have a bad feeling about this.
	# everytime i try to modify a signature,
	# it leads to a decryption failure
	# and not a signature verification failure
	# try forging a signature to see what it returns

	if err or not out: return 1
	return 0


def symmetrically_encrypt(message, key):
	box = SecretBox(key)
	return box.encrypt(message, nonce_generator(SecretBox.NONCE_SIZE))


def symmetrically_decrypt(message, key):
	box = SecretBox(key)
	try:
		return box.decrypt(message)
	except:
		return 1
