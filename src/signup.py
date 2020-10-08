from getpass import getpass

import src.globals
import src.utils
import src.crypto
import src.network
import src.db


def signup():
	# download new server signing keys

	print("\nSignup:")
	print("Type quit to leave.\n")

	# create a keyring and insert the server's public keys
	keys = src.db.fetch_server_keys()
	src.crypto.insert_public_key(keys[0], src.crypto.encryption_key(src.globals.SERVER))
	src.crypto.insert_public_key(keys[1], src.crypto.signature_key(src.globals.SERVER))
	del keys

	while True:

		username = input('Username: ')
		if username == 'quit':
			return
		if src.utils.username_vailidity_checker(username) == 1:
			continue

		rolling_public_key_name = src.utils.random_name_generator()
		if src.crypto.generate_encryption_keys(rolling_public_key_name) == 1:
			return

		nonce = src.crypto.nonce()

		message = {
			"timestamp": src.utils.timestamp(), \
		 	"nonce": nonce, \
			"request_code": src.globals.USERNAME_AVAILABILITY_CHECK, \
			"username": bytes(username, 'utf-8'), \
			"rolling_public_key": src.crypto.fetch_public_keys(rolling_public_key_name)}

		if type(message["rolling_public_key"]) is int:
			return

		request = src.crypto.asymmetrically_encrypt(src.utils.pack(message), \
			src.crypto.encryption_key(src.globals.SERVER))

		request = src.globals.HASH_DENOTER + src.crypto.hash(request) + request

		#with 4 bytes you can represent upto 32 GiB

		request = src.globals.VERSION + src.utils.sizeof(request) + request

		try:
			src.network.send(request)
			response = memoryview(src.network.recieve(src.globals.SMALL_RESPONSE))
		except TypeError:
			# some error message
			continue

		del request

		if response == b'':
			print("Server closed the connection.")

		recieved_hash = response[:src.globals.HASH_SIZE]
		if recieved_hash != src.crypto.hash(response[src.globals.HASH_SIZE:]):
			continue
		else:
			response = response[src.globals.HASH_SIZE:]

		message = src.crypto.validate_asymmetric_response(response, nonce)
		del response

		if message == 1:
			continue

		if message["response_code"] == src.globals.USERNAME_NOT_FOUND:
			n = input("Username available! Signup with this username? [Yes] or no: ")
			if n.lower == 'no' or n.lower() == 'n':
				continue

		elif message["response_code"] == src.globals.USERNAME_FOUND:
			print("Username taken! Choose another username: ")
			continue

		elif message["response_code"] == src.globals.USERNAME_INVALID:
			print("Invalid username! Please try again after sometime...")
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
			if src.utils.password_strength_checker(password) == 0:
				break

		password = bytes(password, 'utf-8')

		if src.crypto.generate_encryption_keys(src.crypto.encryption_key(username)) == 1:
			return

		# sig keys have already been generated
		#if src.crypto.generate_signature_keys(crypto.signature_key(username)) == 1:
		#	return

		nonce = src.crypto.nonce()
		message = {
			"timestamp": src.utils.timestamp(), \
			"nonce": nonce, \
			"request_code": src.globals.SIGNUP, \
			"username": username, \
			"encryption_public_key":  src.crypto.fetch_public_keys(src.crypto.encryption_key(username)), \
			"signature_public_key": src.crypto.fetch_public_keys(src.crypto.signature_key(username))}

		if message["encryption_public_key"] == 1 or message["signature_public_key"] == 1:
			return

		request = src.crypto.asymmetrically_encrypt(src.utils.pack(message), src.crypto.encryption_key(src.globals.SERVER))
		request = src.globals.HASH_DENOTER + src.crypto.hash(request) + request

		request = src.globals.VERSION + src.utils.sizeof(request) + request
		del message


		try:
			src.network.send(request)
			response = memoryview(src.network.recieve(src.globals.SMALL_RESPONSE))
		except TypeError:
			# some error message
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

		message = src.crypto.validate_asymmetric_response(response, nonce)
		if message == 1:
			continue

		if message["response_code"] == src.globals.SIGNUP_SUCCESSFUL:
			# sync with DB now
			if src.db.add_user(username, password) == 0:
				# shred and remove .ccr now
				# introduce a user blocker that prevents user from making more requests?
				print("Signup Successful!\n\n")
			else:
				print("Database Error!")
				print("Signup FAILED!\n\n")
			return
		else:
			print("Recieved invalid response from server. Please retry:")
			continue

		# tell them about our pricing
		# The computation costs to create a signing key
		# will probably prevent bots from spamming. Do something
		# to prevent people from creating multiple accounts
		# without paying up :/
