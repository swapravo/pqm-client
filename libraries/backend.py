def random_name_generator(length=random_name_length):
	return hex(int.from_bytes(urandom(length//2), byteorder=byteorder))[2:]


def timestamp():
	# sync server with NTP
	# unix timestamps are 4 bytes long
	return round(time()).to_bytes(4, byteorder='little')


def encryption_key(username):
	return username + ".qmek"


def signature_key(username):
	return username + ".qmsk"


def _hash(message):
	return blake2b(message, digest_size=hash_size).digest()


def execute(command):

	process = Popen([command], shell=True, stdout=PIPE, stderr=PIPE) #  returns (OUT, ERR)
	returned_data = process.communicate()
	process.terminate()
	out = err = 0
	if returned_data[0] == b'' or returned_data[0] == None:
		out = 0
	else:
		out = returned_data[0]
	if returned_data[1] == b'' or returned_data[1] == None:
		err = 0
	else:
		err = returned_data[1]
	return (out, err)


def mount_ccr_ramdisk(size=1):	# a	cquire file locks!!!
	mkdir('-p', user_home+ccr_folder)
	print("Mounting temporary filesystem. Need sudo access: ")
	with sudo:
		mount("-t", "tmpfs", "-o", "size=" + str(size) + "M", "tmpfs", user_home+ccr_folder)


def unmount_ccr_ramdisk():
	for _file in listdir(user_home+ccr_folder):
		if isfile(user_home+ccr_folder+_file):
			shred("-vfzu", user_home+ccr_folder+_file)
	print("Unmounting temporary filesystem. Require sudo access:")
	with sudo:
		umount("-dvfl", user_home+ccr_folder)
	rm("-rfv", user_home+ccr_folder)


def generate_encryption_keys(keyname):
	print("Generating asymmetric encryption keys.")
	print("THESE FILES NEED TO BE (f)LOCKED!!!")
	out, err = execute("./libraries/ccr --gen-key ENC-256 --name " + keyname)
	if not bytes("Gathering random seed bits from kernel", 'utf-8') in err:
		print(err)
		return 1
	return keyname


def generate_signature_keys(keyname):
	print("Generating signing Keys. This is going to take a while.")
	print("THESE FILES NEED TO BE (f)LOCKED!!!")
	out, err = execute("./libraries/ccr --gen-key SIG-256 --name " + keyname)
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

	out, err = execute("./libraries/ccr -" + mode + " --fingerprint -F " + keyname)
	if err: return 1
	return bytes.fromhex(''.join(str(out[-81:-2], 'utf-8').split(':')))


def asymmetrically_encrypt(message, public_key_name):

	if type(message) != bytes:
		message = bytes(message, 'utf-8')

	process = Popen(["./libraries/ccr -e -r " + public_key_name], shell=True, stdout=PIPE, stdin=PIPE)
	returned_data = process.communicate(input=message)
	process.terminate()

	#codecrypt returns a None if the encryption is successful
	if returned_data[1] == None:
		return returned_data[0]
	return 1


def asymmetrically_decrypt(message, private_key_name):

	#handle decryption failures => wrong/missing private key

	#if type(message) != bytes:
	#	message = bytes(message, 'utf-8')

	process = Popen(["./libraries/ccr -d -r " + private_key_name], shell=True, stdout=PIPE, stdin=PIPE)
	returned_data = process.communicate(input=message)
	process.terminate()

	if returned_data[0] == b'':
		return 1
	return returned_data[0]


def symmetrically_encrypt(message, key):
	box = xsalsa20poly1305(key)
	return box.encrypt(message, nonce_generator(xsalsa20poly1305.NONCE_SIZE))


def symmetrically_decrypt(message, key):
	box = xsalsa20poly1305(key)
	return box.decrypt(message)

def sign(message, recipient_name):
	process = Popen(["./ccr -s -r " + recipient_name], shell=True, stdout=PIPE, stdin=PIPE)
	returned_data = process.communicate(input=message)
	process.terminate()

	if returned_data[0] == b'':
		return 1
	return returned_data[0]


def verify_signature(signature):
	# the key must be in the ccr folder!
	process = Popen(["./ccr -v "], shell=True, stdout=PIPE, stdin=PIPE)
	returned_data = process.communicate(input=signature)
	process.terminate()

	if not returned_data[0] == b'':
		return 1
	return returned_data[0]


def lock_user_keys(username, password):

	if type(password) != bytes:
		password = bytes(password, 'utf-8')

	blake_hash = blake2b(password).hexdigest()
	whirlpool_hash = whirlpool(password).hexdigest()
	sha512_hash = sha512(password).hexdigest()

	touch(user_home+ccr_folder+username)
	execute("7z a {} {} -mhe -p{}".format(user_home+ccr_folder+username+"temp1", user_home+ccr_folder+"*", sha512_hash))
	execute("7z a {} {} -mhe -p{}".format(user_home+ccr_folder+username+"temp2", user_home+ccr_folder+username+"temp1.7z", whirlpool_hash))
	shred("-vfz", user_home+ccr_folder+username+"temp1.7z")
	rm("-fv", user_home+ccr_folder+username+"temp1.7z")
	print("SAVE KEYS INSIDE A DATABASE OR ATLEAST INSIDE /libraries/keys/")
	execute("7z a ./keys/{} {} -mhe -p{}".format(username, user_home+ccr_folder+username+"temp2.7z", blake_hash))
	shred("-vfz", user_home+ccr_folder+username+"temp2.7z")
	rm("-fv", user_home+ccr_folder+username+"temp2.7z")

	return 0


def unlock_user_keys(username, password):

	if type(password) != bytes:
		password = bytes(password, 'utf-8')

	blake_hash = blake2b(password).hexdigest()
	whirlpool_hash = whirlpool(password).hexdigest()
	sha512_hash = sha512(password).hexdigest()

	print("READ KEYS FROM A DATABASE OR ATLEAST FROM ./libraries/keys/")

	"""
	out, err = execute("7z e ./keys/{} -o{} -p{}".format(username+'.7z', user_home+ccr_folder,  blake_hash))
	if err: return 1
	out, err = execute("7z e {} -o{} -p{}".format(user_home+ccr_folder+username+'temp2.7z', user_home+ccr_folder,  whirlpool_hash))
	shred('-vfz', user_home+ccr_folder+username+"temp2.7z")
	rm('-fv', user_home+ccr_folder+username+"temp2.7z")
	if err: return 1
	out, err = execute("7z e {} -o{} -p{}".format(user_home+ccr_folder+username+'temp1.7z', user_home+ccr_folder,  sha512_hash))
	if err: return 1
	shred('-vfz', user_home+ccr_folder+username+"temp1.7z")
	rm('-fv', user_home+ccr_folder+username+"temp1.7z")
	"""
	return 0


def username_vailidity_checker(username):

	# check for curse words, commands, illegal symbols
	if len(username) < 3 or len(username) > 128:
		print("Username must be atleast four and less than 129 charcters.")
		return 1

	username = username.lower()
	allowed_characters = printable[:36] + '_.'
	cleaned_username = ''.join(list(filter(lambda x: x in allowed_characters, username)))

	if username != cleaned_username:
		print("Illegal characters present. Allowed charcters: ", ' '.join(list(allowed_characters)))
		return 1

	return 0


def password_strength_checker(password):

	print("REMOVE THIS RETURN STATEMENT. FOR DEVELOPMENT PURPOSES ONLY!!!")
	return 0

	# alteast 128 bits of entropy required => 20 characters atleast
	# log2(26 + 26 + 10 + 33)

	if len(password) < 20:
		print("Not enough Entropy. Password needs to be longer.")
		return 1
	if contains("[a-z]", password) == None:
		print("Small letters needed.")
		return 1
	if contains("[A-Z]", password) == None:
		print("Capital letters needed.")
		return 1
	if contains("[0-9]", password) == None:
		print("Numbers needed.")
		return 1
	if contains("[" + printable[62:-5] + "]", password) == None:
		print("Special characters needed.")
		return 1
	print("Your password's entropy: about", len(password) * 6.5, "bits.")
	return 0
