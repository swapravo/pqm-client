from subprocess import Popen, PIPE, call
from os import urandom, listdir
from os.path import isfile, getsize
from time import time
from sh import mkdir, mount, shred, umount, rm
from msgpack import packb, unpackb
from sh.contrib import sudo
from re import search as contains
from string import printable
from sys import byteorder
from shlex import split, quote
from tempfile import mkstemp, mkdtemp
from datetime import datetime
import tzlocal

import src.globals


def sizeof(message):
	#with 4 bytes you can represent upto 32 GiB
	return (len(message)).to_bytes(4, byteorder='little')


def pack(message):
	return packb(message, use_bin_type=True)


def unpack(message):
	try:
		return unpackb(message, raw=False)
	except:
		print("Invalid message! Unpacking message FAILED!")
		return None


def random_name_generator(length=src.globals.RANDOM_NAME_LENGTH):
	return hex(int.from_bytes(urandom(length//2), byteorder=byteorder))[2:]


def timestamp():
	# sync server with NTP
	# unix timestamps are 4 bytes long
	return round(time())


def date(timestamp):
    return (datetime.utcfromtimestamp(timestamp) + tzlocal.get_localzone().utcoffset(datetime.now())).strftime("%A, %d. %B %Y %I:%M%p")


def message_id():
	src.globals.MESSAGE_ID += 1
	return src.globals.MESSAGE_ID


def execute(command, data=None):
	# I AM AWARE THAT THIS IS FLAGGED AS A VULNERABILITY.
	# Setting shell=False should fix this but that leads to
	# command parsing problems
	# SANITIZE COMMANDS HERE
	process = Popen([command], shell=True, stdout=PIPE, stdin=PIPE)
	if data:
		if type(data) != bytes:
			print(data)
		returned_data = process.communicate(input=data)
	else:
		returned_data = process.communicate()
	process.terminate()

	out, err = None, None
	if returned_data[0]:
		out = returned_data[0]
	if returned_data[1]:
		err = returned_data[1]
	return (out, err)


def mount_ramdisk(size=1):
	# acquire file locks!!!
	# use umask
	mkdir('-p', src.globals.USER_HOME+src.globals.CCR_FOLDER)
	print("Mounting temporary filesystem. Need sudo access: ")
	with sudo:
		mount("-t", "tmpfs", "-o", "size=" + str(size) + "M", "tmpfs", \
			src.globals.USER_HOME+src.globals.CCR_FOLDER)


def unmount_ramdisk():
	for _file in listdir(src.globals.USER_HOME+src.utils.CCR_FOLDER):
		if isfile(src.globals.USER_HOME+src.globals.CCR_FOLDER):
			shred("-vfzu", src.globals.USER_HOME+src.globals.CCR_FOLDER)
	print("Unmounting temporary filesystem. Require sudo access:")
	with sudo:
		umount("-dvfl", src.globals.USER_HOME+src.globals.CCR_FOLDER)
	rm("-rfv", src.globals.USER_HOME+src.globals.CCR_FOLDER)


def username_is_vailid(username):
	# check for curse words, commands, illegal symbols
	if len(username) < 3 or len(username) > 128:
		print("Username must be atleast four and less than 129 charcters.")
		return False
	username = username.lower()
	allowed_characters = printable[:36] + '_.'
	cleaned_username = ''.join(list(filter(lambda x: x in allowed_characters, \
		username)))

	if username != cleaned_username:
		print("Illegal characters present. Allowed charcters: ", \
			' '.join(list(allowed_characters)))
		return False
	return True


def password_is_strong(password):
	print("Bypassing password strength check!")
	return True
	# alteast 128 bits of entropy required => 20 characters atleast
	# log2(26 + 26 + 10 + 33)
	if len(password) < 20:
		print("Not enough Entropy. Password needs to be longer!")
		return False
	if contains("[a-z]", password) is None:
		print("Small letters needed!")
		return False
	if contains("[A-Z]", password) is None:
		print("Capital letters needed!")
		return False
	if contains("[0-9]", password) is None:
		print("Numbers needed!")
		return False
	if contains("[" + printable[62:-5] + "]", password) is None:
		print("Special characters needed!")
		return False
	print("Your password's entropy: about", len(password) * 6.5, "bits.")
	return True


def issqlite3(path):
	if not isfile(path):
		return False
	if getsize(filename) < 100:
		return False
	with open(path, 'rb') as fo:
		header = fo.read(100)
		return header[:16] == b'SQLite format 3\x00'


def mount_temp_directory():
	return mkdtemp(dir=src.globals.USER_HOME+src.globals.CCR_FOLDER)


def writer(message=None):
	if message:
		_ = input(message+'\nPress enter to continue...\n')
	fo = mkstemp(dir=src.globals.TEMP_FOLDER)
	call(['nano', fo[1]])
	with open(fo[1]) as _fo:
		return _fo.read()


def email_is_valid(address):
	address = address.split('@')
	if len(address) == 2:
		return username_is_vailid(address[0]) and address[1] in src.globals.VALID_DOMAINS
	return False
