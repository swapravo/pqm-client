from os import urandom
from getpass import getpass
from sys import byteorder
from msgpack import packb as pack, unpackb as unpack
from time import sleep


import src.globals
import src.utils
import src.crypto
import src.network
import src.db

def signup():
	# download new server signing keys

	print("\nSignup:")
	print("Type quit to leave.\n")

	while True:

		username = input('Username: ')
		if username == 'quit':
			return
		if src.utils.username_vailidity_checker(username) == 1:
			continue

		nonce = urandom(src.globals.NONCE_SIZE)
		plaintext = {"timestamp": src.utils.timestamp(), "nonce": nonce, \
			"request_code": src.globals.USERNAME_AVAILABILITY_CHECK, "username": bytes(username, 'utf-8')}

		rolling_public_key_name = src.utils.random_name_generator()
		if src.crypto.generate_encryption_keys(rolling_public_key_name) == 1:
			print("Asymmetric key generation failed.")
			return

		# make sure this key is written to ~/.ccr/ which should be a ramdisk
		plaintext["rolling_public_key"] = src.utils.execute("./src/ccr -p -F " + rolling_public_key_name)[0]

		payload = src.crypto.asymmetrically_encrypt(pack(plaintext, use_bin_type=True), src.crypto.encryption_key(src.globals.SERVER))

		payload = src.globals.HASH_DENOTER + src.crypto.hash(payload) + payload
		#with 4 bytes you can represent upto 32 GiB
		payload_size = (len(payload)).to_bytes(4, byteorder='little')

		request = src.globals.VERSION + payload_size + payload
		del payload

		try:
			src.network.send(request)

			response = memoryview(src.network.recieve(src.globals.USERNAME_AVAILABILITY_CHECK_RESPONSE_SIZE))
		except TypeError:
			if response == 1:
				print("Network Problem...")
			# if response == 2:
				# print("Server timeout...")

		print("Recieved ", response.nbytes, "bytes of data from the server.")

		if response == b'':
			print("Server closed the connection.")

		recieved_hash = response[:src.globals.HASH_SIZE]

		if recieved_hash != src.crypto.hash(response[src.globals.HASH_SIZE:]):
			print("Hash verification FAILED!. Please retry!")
			continue
		else:
			response = response[src.globals.HASH_SIZE:]

		# check for decryption errors
		plaintext = src.crypto.asymmetrically_decrypt(response, rolling_public_key_name)
		if plaintext == 1:
			print("Decryption FAILED!. Please Retry!")
			continue

		plaintext = unpack(plaintext, raw=False)

		if plaintext["nonce"] != nonce:
			print("Recieved nonce does not match nonce sent!")
			continue

		if plaintext["response_code"] == src.globals.USERNAME_NOT_FOUND:
			n = input("Username available! Signup with this username? [Yes] or no: ")
			if n.lower == 'no' or n.lower() == 'n':
				continue
		elif plaintext["response_code"] == username_found_code:
			print("Username taken! Choose another username: ")
			continue
		elif plaintext["response_code"] == username_invalid_code:
			print("Invalid username! Please try again after sometime...")
			# introduce a user blocker that prevents user from making more requests?
			continue
		else:
			print("Recieved invalid response from server. Please retry:")
			continue


		while True:
			password = getpass()
			if password == "quit":
				# remove the enc keys!
				# inform the server to drop the request
				return
			response = src.utils.password_strength_checker(password)
			if response == 0:
				break

		password = bytes(password, 'utf-8')
		# catch and deal with errors in a manner a bit more robust :/
		if src.crypto.generate_encryption_keys(src.crypto.encryption_key(username)) == 1:
			print("Asymmetric key generation failed!")
			return

		# sig keys have already been generated
		#if src.crypto.generate_signature_keys(crypto.signature_key(username)) == 1:
		#	print("Signature key generation failed.")
		#	return

		nonce = urandom(src.globals.NONCE_SIZE)
		plaintext = {"timestamp": src.utils.timestamp(), "nonce": nonce, \
			"request_code": src.globals.SIGNUP, "username": username}
		plaintext["encryption_public_key"] =  src.utils.execute("./src/ccr -p -F " + src.crypto.encryption_key(username))[0]
		plaintext["signature_public_key"] = src.utils.execute("./src/ccr -p -F " + src.crypto.signature_key(username))[0]

		payload = src.crypto.asymmetrically_encrypt(pack(plaintext, use_bin_type=True), src.crypto.encryption_key(src.globals.SERVER))
		payload = src.globals.HASH_DENOTER + src.crypto.hash(payload) + payload
		payload_size = (len(payload)).to_bytes(4, byteorder='little')

		request = src.globals.VERSION + payload_size + payload
		del payload


		try:
			src.network.send(request)
			response = memoryview(src.network.recieve(src.globals.USERNAME_AVAILABILITY_CHECK_RESPONSE_SIZE))
		except TypeError:
			if response == 1:
				print("Network Problem...")
			# if response == 2:
				# print("Server timeout...")

		print("Recieved ", response.nbytes, "bytes of data from the server.")

		if response == b'':
			print("Server closed the connection.")
			return

		recieved_hash = response[:src.globals.HASH_SIZE]

		if recieved_hash != src.crypto.hash(response[src.globals.HASH_SIZE:]):
			print("Hash verification FAILED!. Please retry!")
			continue
		else:
			response = response[src.globals.HASH_SIZE:]

		# check for decryption errors
		plaintext = src.crypto.asymmetrically_decrypt(response, rolling_public_key_name)
		if plaintext == 1:
			print("Decryption FAILED!. Please Retry!")
			continue

		plaintext = unpack(plaintext, raw=False)

		if plaintext["nonce"] != nonce:
			print("Recieved nonce does not match nonce sent. Please retry!")
			continue
		elif plaintext["response_code"] == src.globals.SIGNUP_SUCCESSFUL:
			# sync with DB now
			if src.db.add_user(username, password, \
				src.utils.execute("./src/ccr -y -P -F " + src.crypto.encryption_key(username))[0], \
				src.utils.execute("./src/ccr -y -P -F " + src.crypto.signature_key(username))[0]) == 0:
				# introduce a user blocker that prevents user from making more requests?
				print("Signup Successful!\n\n")
			else:
				print("Database Error!")
				print("Signup FAILED!\n\n")
			return
		else:
			print("Recieved invalid response from server. Please retry:")
			print(plaintext)
			continue

		# tell them about our pricing
		# The computation costs to create a signing key
		# will probably prevent bots from spamming. Do something
		# to prevent people from creating multiple accounts
		# without paying up :/


def login():

	"""
	first check whether the user exists on this computer or not.
	if it does, decrypt, connect to the server to authenticate & synchronise
	else, check whether the user exists on the server and
	authenticate and sync him


	As a later feature, the
	user will get to choose whether he wants to send his
	(symmetric and asymmetric) keys encrypted with his
	symmetric password over to our server.
	The default option provides the user more freedom over his keys
	at the cost of portability. (he will still be allowed to manually
	export his keys to portable storage devices of his choice like before)
	If the user chooses the latter,
	we shall need a method to establish that he will be able to decrypt
	the encrypted passwords we are holding for him.


	# Login should be a two step process. Firstly, the client-side login
	# Secondly, server-side login.
	"""

	# client-side login

	i = 0
	print("Login:")
	print("Type quit to leave.")
	while True:
		username = input('username: ')
		if username == "quit":
			return
		password = getpass()
		if password == "quit":
			return
		response = unlock_user_keys(username, password)
		if not response:
			print("Client-side Login Successful.")
			break
		print("Wrong username/password. Sleeping for ", str(2 ** i), "seconds.")
		sleep(2 ** i)
		i += 1


	# server-side login

	if server_side_login(username) == 0:
		print("Server-side Login Successful.")
		return 0
	else:
		print("Server-side Login Failed.")
		return 1