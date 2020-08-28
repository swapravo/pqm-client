def signup():


	# download new server signing keys

	print("\nSignup:")
	print("Type quit to leave.\n")

	while True:

		username = input('Username: ')
		if username == 'quit':
			return
		if username_vailidity_checker(username) == 1:
			continue

		# checking the availablity of this username
		# creating the request

		# size of the request: ???

		# 1.
		# asymmetric_byte

		# 2.
		timestamp_ = timestamp()

		# 3.
		nonce = urandom(nonce_size)

		# 4.
		request_code = username_availability_check_code

		# 5.
		username_ = bytes(max_username_size - len(username)) + bytes(username, 'utf-8')

		# 6.
		rolling_public_key_name = random_name_generator()
		if generate_asymmetric_keys(rolling_public_key_name) == 1:
			print("Asymmetric key generation failed.")
			return
		else:
			print("Temporary Key created: ", rolling_public_key_name)

		# make sure this key is written to ~/.ccr/
		rolling_public_key = execute("./libraries/ccr -p -F " + rolling_public_key_name)[0]

		plaintext = timestamp_ + nonce + request_code + username_ + rolling_public_key

		"""
		print(timestamp_)
		print(nonce)
		print(request)
		print(username_)
		print(rolling_public_key)
		"""

		# 7.
		hash_ = _hash(plaintext)

		# print(hash_)

		request = asymmetric_byte + asymmetrically_encrypt(plaintext, encryption_key(server)) + hash_

		# assert len(request) < username_availability_check_request_size

		from hashlib import md5
		print("Sending ", len(request), "bytes of data to the server. Hash: ", md5(request).hexdigest())

		try:
			response = memoryview(send(request, username_availability_check_response_size))
		except TypeError:
			if response == 1:
				print("Network Problem...")
			# if response == 2:
				# print("Server timeout...")

		print("Recieved ", response.nbytes, "bytes of data from the server.")

		if response == b'':
			print("Server closed the connection.")

		# parsing the response
		# what do i do when these errors occur???

		recieved_asymmetric_byte = response[:header_byte_size]

		if recieved_asymmetric_byte != asymmetric_byte:
			print("Garbage recieved from server!\n")
			print("Garbage: ", response)
			return

		# noting the hash
		recieved_hash = response[-hash_size:]

		# check for decryption errors
		response = asymmetrically_decrypt(response[header_byte_size:-hash_size], rolling_public_key_name)
		if response == 1:
			print("decryption FAILED!")
			continue

		# assuming the decryption was succesful
		response = memoryview(response)

		if _hash(response) != recieved_hash:
			print("Message authentication failed!")
			continue

		recieved_request_code = response[:request_code_size]
		if recieved_request_code != request_code:
			print("Request code mismatch!\n", request_code, recieved_request_code.tobytes())
			continue

		recieved_nonce = response[request_code_size:request_code_size+nonce_size]
		if recieved_nonce != nonce:
			print("Recieved nonce does not match nonce sent!")
			continue

		recieved_response_code = response[request_code_size+nonce_size:request_code_size+nonce_size+response_code_size]

		if recieved_response_code == username_not_found_code:
			n = input("Username available! Signup with this username? [Yes] or no: ")
			if n.lower != 'no' or n.lower() != 'n':
				break
		elif recieved_response_code == username_found_code:
			print("Username taken! Choose another username: ")
			continue
		elif recieved_response_code == username_invalid_code:
			print("Invalid username! Please try again after sometime...")
			# introduce a user blocker that prevents user from making more requests?
			continue
		else:
			print("Recieved invalid response from server. Please retry:")
			continue


	while True:
		password = getpass()
		if password == "quit":
			# remove that enc key!
			# inform the server to drop the request
			return
		response = password_strength_checker(password)
		if response == 0:
			break


	# catch and deal with errors in a manner a bit more robust :/
	if generate_asymmetric_keys(encryption_key(username)) == 1:
		print("Asymmetric key generation failed!")
		return

	print("SKIPPING THE GENERATION OF THE SIGNING KEYS FOR NOW!!!")
	print("Using asy enc key as sig key...")

#	if generate_signature_keys(signature_key(username)) == 1:
#		print("Signature key generation failed.")
#		return


	# creating the signup request

	# 1. asymmetric_byte

	# 2.
	timestamp_ = timestamp()

	# 3.
	nonce = urandom(nonce_size)

	# 4.
	request_code = signup_code

	# 5. username_ remains the same

	# 7.
	public_key_1 = execute("./libraries/ccr -p -F " + encryption_key(username))[0]

	# 6.
	encryption_public_key_size = (len(public_key_1)).to_bytes(max_encryption_public_key_size, byteorder='little')

	# 9.
	public_key_2 = execute("./libraries/ccr -p -F " + encryption_key(username+'_'))[0] #execute("./libraries/ccr -p -F " + signature_key(username))[0]

	# 8.
	signature_public_key_size = (len(public_key_2)).to_bytes(max_signature_public_key_size, byteorder='little')

	"""
	print(timestamp_)
	print(nonce)
	print(request_code)
	print(username_)
	print(encryption_public_key_size)
	print(public_key_1)
	print(signature_public_key_size)
	print(public_key_2)
	"""

	plaintext = timestamp_ + nonce + request_code + username_ + encryption_public_key_size + public_key_1 + signature_public_key_size + public_key_2

	# 10.
	hash_ = _hash(plaintext)

	request = asymmetric_byte + asymmetrically_encrypt(plaintext, encryption_key(server)) + hash_

	#assert len(request) < signup_request_size

	print("Signup Request:\n", request)
	print("Length of request: ", len(request))

	try:
		response = memoryview(send(request, username_availability_check_response_size))
	except TypeError:
		if response == 1:
			print("Network Problem...")
		# if response == 2:
			# print("Server timeout...")

	print("size of response: ", len(response))

	recieved_asymmetric_byte = response[:header_byte_size]
	if recieved_asymmetric_byte != asymmetric_byte:
		print("Garbage recieved from server!\n")
		return

	# noting the hash
	recieved_hash = response[-hash_size:]

	# check for decryption errors
	response = asymmetrically_decrypt(response[header_byte_size:-hash_size], encryption_key(username))

	# assuming the decryption was succesful
	response = memoryview(response)

	if _hash(response) != recieved_hash:
		print("Message authentication failed!")
		return

	recieved_request_code = response[header_byte_size:header_byte_size+request_code_size]
	if recieved_request_code != request:
		print("Request code mismatch!\n")
		return

	recieved_nonce = response[header_byte_size+request_code_size:header_byte_size+request_code_size+nonce_size]
	if recieved_nonce != nonce:
		print("Recieved nonce does not match nonce sent!")
		return

	recieved_response_code = response[header_byte_size+request_code_size+nonce_size:header_byte_size+request_code_size+nonce_size+response_code_size]
	if response == signup_success_code:
		lock_user_keys(username, password)
		print("Signup succesful!")
	elif response == signup_failed_code:
		print("Signup failed!")

	# tell them about our pricing
	# The computation costs to create a signing key
	# will probably prevent bots from spamming. Do something
	# to prevent people from creating multiple accounts
	# without paying up :/

"""

def login():


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

"""
