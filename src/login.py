from getpass import getpass
from time import sleep

import src.globals
import src.utils
import src.crypto
import src.network
import src.db


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
		response = src.db.authenticate_user(username, password)
		if not response:
			src.globals.USERNAME = username
			src.globals.PASSWORD = password
			# src.globals.LOGGGED_IN = True
			# after server side login
			print("Client-side Login Successful.")
			break
		print("Wrong username/password. Sleeping for ", str(2 ** i), "seconds.")
		sleep(2 ** i)
		i += 1

		nonce = src.utils.nonce()
		message = {
			"timestamp": src.utils.timestamp(), \
			"nonce": nonce, \
			"request_code": src.globals.LOGIN_STEP_1, \
			"username": src.globals.USERNAME}

		request = src.crypto.asymmetrically_encrypt(src.utils.pack(message), \
			src.crypto.encryption_key(src.globals.SERVER))

		del message

		request = src.globals.SIGNATURE_DENOTER + src.crypto.sign(src.crypto.hash(request), \
			src.globals.SERVER) + request

		request = src.globals.VERSION + src.utils.sizeof(request) + request

		try:
			src.network.send(request)
			response = memoryview(src.network.recieve(src.globals.RESPONSE_SIZE)) #NO NOT USERNAME AVAIL
		except TypeError:
			continue

		del request

		if response == b'':
			print("Server closed the connection.")
			return

		recieved_hash = response[:src.globals.HASH_SIZE]
		if recieved_hash != src.crypto.hash(response[src.globals.HASH_SIZE:]):
			print("Hash verification FAILED!. Please retry!")
			continue
		else:
			response = response[src.globals.HASH_SIZE:]

		message = src.utils.validate_asymmetric_response(response, nonce)
		if message == 1:
			continue

		if message["response_code"] != src.globals.OKAY:
			print("Login FAILED! Please retry!")
			continue
		else:
			key = src.crypto.symmetric_key_generator()

			message = {
				"timestamp": timestamp(), \
				"request_code:": src.globals.LOGIN_STEP_2, \
				"nonce": message["nonce2"], \
				"symmetric_key": key}

		request = src.crypto.asymmetrically_encrypt(src.utils.pack(message), \
			src.crypto.encryption_key(src.globals.SERVER))
		del request

		signature = src.crypto.sign(src.crypto.hash(request), src.globals.SERVER)
		if signature == 1:
			continue

		request = src.globals.SIGNATURE_DENOTER + src.utils.sizeof(signature) + request

		request = src.globals.VERSION + src.utils.sizeof(request) + request

		del message, signature

		try:
			src.network.send(request)
			response = memoryview(src.network.recieve(src.globals.RESPONSE_SIZE))
		except TypeError:
			# some error message
			continue

		del request

		if response == b'':
			print("Server closed the connection.")
			return

		# VERIFY SIGNATURE HERE

		message = src.utils.validate_asymmetric_response(response)
		if message:
			return

		src.globals.ROLLING_ID = message["rolling_id"]
		src.globals.ROLLING_AUTHENTICATION_TOKEN = message["rolling_authentication_token"]
		src.globals.KEY = key
		print("Server-side login SUCCESSFULL!")
		del message
