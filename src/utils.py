from subprocess import Popen, PIPE
from os import urandom, listdir
from time import time
from sh import mkdir, mount, shred, umount, rm, touch
from msgpack import packb, unpackb
from sh.contrib import sudo
from re import search as contains
from string import printable
from sys import byteorder


import src.globals


def sizeof(message):
	return (len(message)).to_bytes(4, byteorder='little')


def pack(message):
	return packb(message, use_bin_type=True)


def unpack(message):
	try:
		return unpackb(message, raw=False)
	except:
		print("Invalid message! Message unpacking FAILED!")
		return 1


def random_name_generator(length=src.globals.RANDOM_NAME_LENGTH):
	return hex(int.from_bytes(urandom(length//2), byteorder=byteorder))[2:]


def timestamp():
	# sync server with NTP
	# unix timestamps are 4 bytes long
	return round(time()).to_bytes(4, byteorder='little')


def message_id():
	src.globals.MESSAGE_ID += 1
	return src.globals.MESSAGE_ID


def execute(command, data=None):
    # SANITIZE command

	if data:
		process = Popen([command], shell=True, stdout=PIPE, stdin=PIPE)
		returned_data = process.communicate(input=data)
	else:
		process = Popen([command], shell=True, stdout=PIPE, stderr=PIPE)
		returned_data = process.communicate()

	process.terminate()
	out = err = 0
	if returned_data[0] == b'' or returned_data[0] is None:
		out = 0
	else:
		out = returned_data[0]
	if returned_data[1] == b'' or returned_data[1] is None:
		err = 0
	else:
		err = returned_data[1]
	return (out, err)


def mount_ramdisk(size=1):	# a	cquire file locks!!!
	mkdir('-p', user_home+ccr_folder)
	print("Mounting temporary filesystem. Need sudo access: ")
	with sudo:
		mount("-t", "tmpfs", "-o", "size=" + str(size) + "M", "tmpfs", user_home+ccr_folder)


def unmount_ramdisk():
	for _file in listdir(user_home+ccr_folder):
		if isfile(user_home+ccr_folder+_file):
			shred("-vfzu", user_home+ccr_folder+_file)
	print("Unmounting temporary filesystem. Require sudo access:")
	with sudo:
		umount("-dvfl", user_home+ccr_folder)
	rm("-rfv", user_home+ccr_folder)


def username_vailidity_checker(username):

	# USE THE STANDARD

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
		print("Not enough Entropy. Password needs to be longer!")
		return 1
	if contains("[a-z]", password) is None:
		print("Small letters needed!")
		return 1
	if contains("[A-Z]", password) is None:
		print("Capital letters needed!")
		return 1
	if contains("[0-9]", password) is None:
		print("Numbers needed!")
		return 1
	if contains("[" + printable[62:-5] + "]", password) is None:
		print("Special characters needed!")
		return 1
	print("Your password's entropy: about", len(password) * 6.5, "bits.")
	return 0
