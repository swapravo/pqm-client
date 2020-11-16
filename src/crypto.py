from os import urandom
from sys import byteorder
from hashlib import blake2b
from nacl.pwhash.argon2id import kdf
from nacl.secret import SecretBox #xsalsa20poly1305
from nacl.utils import random as nacl_random

import src.globals
import src.utils


def nonce(size=src.globals.NONCE_SIZE):
	return urandom(size)


def encryption_key(username):
	return username + ".qmek"


def signature_key(username):
	return username + ".qmsk"


def hash(message):
	return blake2b(message, digest_size=src.globals.HASH_SIZE).digest()


def insert_public_key(key, keyname):
	out, err = src.utils.execute("./src/ccr -y -i --name " + keyname, key)
	if err or out:
		print("Public key insertion FAILED! Codecrypt returned:", err)
	return (out, err)


def insert_private_key(key, keyname):
	out, err = src.utils.execute("./src/ccr -y -I --name " + keyname, key)
	if err or out:
		print("Private key insertion FAILED! Codecrypt returned:", err)
	return (out, err)


def key_exists_in_keyring(keyname):
	# check if Codecrypt's keyring has any
	# key named keyname
	return False


def fetch_public_keys(keyname):
	out, err = src.utils.execute("./src/ccr -p -F " + keyname)
	if err:
		print("Public key NOT FOUND! Codecrypt returned:", err)
	return (out, err)


def remove_public_key(keyname):
	out, err = src.utils.execute("./src/ccr -y -x " + keyname)
	if err or out:
		print("Public key removal FAILED! Codecrypt returned:", err)
	return (out, err)


def remove_private_key(keyname):
	out, err = src.utils.execute("./src/ccr -y -X " + keyname)
	if err or out:
		print("Private key removal FAILED! Codecrypt returned:", err)
	return (out, err)


def generate_encryption_keys(keyname):
	out, err = src.utils.execute("./src/ccr --gen-key ENC-256 --name " + keyname)
	if err and not bytes("Gathering random seed bits from kernel", 'utf-8') in err:
		print("Public key generation FAILED! Codecrypt returned:", err)
		return (out, err)
	out, err = keyname, None
	return (out, err)


def generate_signature_keys(keyname):
	out, err = src.utils.execute("./src/ccr --gen-key SIG-256 --name " + keyname)
	if err and not bytes("Gathering random seed bits from kernel", 'utf-8') in err:
		print("Signature key generation FAILED! Codecrypt returned:", err)
		return (out, err)
	out, err = keyname, None
	return (out, err)


def key_is_valid(key, key_is_public=True):
	if key_is_public:
	# for public keys
		out, err = src.utils.execute("./ccr -n -i --name " + src.utils.random_name_generator(), key)
	# for private keys
	else:
		out, err = src.utils.execute("./ccr -n -I --name " + src.utils.random_name_generator(),  key)
	if err:
		return False
	return True


def key_fingerprint(keyname):

	out, err = None, None

	if keyname[-2] == 'p':
		mode = 'k'
	elif keyname[-2] == 's':
		mode = 'K'
	else:
		(out, err)

	out, err = src.utils.execute("./src/ccr -" + mode + " --fingerprint -F " + keyname)
	if err:
		print("Key fingerprinting FAILED!! Codecrypt returned:", err)
	else:
		out = bytes.fromhex(''.join(str(out[-81:-2], 'utf-8').split(':')))
		err = 0
	return (out, err)


def asymmetrically_encrypt(message, public_key_name):

	out, err = src.utils.execute("./src/ccr -e -r " + public_key_name, message)

	if not out or err:
		print("Asymmetric encryption FAILED! Codecrypt returned:")
		err = 1
	else:
		err = 0
	return (out, err)


def asymmetrically_decrypt(message, private_key_name):

	out, err = src.utils.execute("./src/ccr -d -r " + private_key_name, message)

	if not out or err:
		print("Asymmetric decryption FAILED! Codecrypt returned:")
		err = 1
	else:
		err = 0
	return (out, err)


def sign(message, recipient_name):

	out, err = src.utils.execute("./src/ccr -s -r " + recipient_name, message)

	if err:
		print("Signing FAILED! Codecrypt returned:", err)
		err = 1
	else:
		err = 0
	return (out, err)


def verify_signature(signature):
	out, err = src.utils.execute("./src/ccr -v ", signature)

	# i have a bad feeling about this.
	# everytime i try to modify a signature,
	# it leads to a decryption failure
	# and not a signature verification failure
	# try forging a signature to see what it returns

	if err or not out:
		print("Signature Verification FAILED! Codecrypt returned:", err)
		err = 1
	else:
		err = 0
	return (out, err)


def validate_asymmetric_response(message, nonce):

	out, err = asymmetrically_decrypt(message, src.globals.SERVER)
	if err:
		return (out, err)

	out = src.utils.unpack(out)
	if out is None:
		return (None, 1)

	if out["nonce"] != nonce:
		out = None

	return (out, err)


def symmetric_key_generator():
	return nacl_random(SecretBox.KEY_SIZE)


def symmetrically_encrypt(message, key):
	box = SecretBox(key)
	return box.encrypt(message, nacl_random(SecretBox.NONCE_SIZE))


def symmetrically_decrypt(message, key):
	try:
		box = SecretBox(key)
		return box.decrypt(message)
	except:
		print("Symmetric decryption FAILED!")
		return None
