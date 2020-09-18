from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from os import urandom, listdir
from os.path import isfile
from sys import byteorder, exit
from sqlite3 import connect as db_connector
from hashlib import blake2b
from nacl.pwhash.argon2id import kdf
from nacl.secret import SecretBox as xsalsa20poly1305
from nacl.utils import random as nonce_generator
from hmac import compare_digest # IMPLEMENT THIS !!!
from pathlib import Path
from subprocess import Popen, PIPE
from sh import mkdir, mount, shred, umount, rm, touch
from sh.contrib import sudo
from msgpack import packb as pack, unpackb as unpack
from time import time, sleep
from string import printable
from re import search as contains
from getpass import getpass


# global variables

signature_denoter = b'\x00' #10101010

hash_denoter = b'\xff'     #01010101

loggged_in = False

username = ''

password = ''

server = "server"

server_ip = "127.0.0.1"

server_port = 9000

ccr_folder = ".ccr/"

user_home = str(Path.home())+'/'

version = b'\x00\x00'

random_name_length = 16 # characters in hex

nonce_size = 32

hash_size = 32

# UNIX timestamps
timestamp_size = 4

max_allowable_time_delta = 60 # seconds. a proper value needs to set according to network requirements

max_username_size = 64

message_id_size = 2

request_code_size = 2

response_code_size = 2

rolling_id_size = 8

rolling_authentication_token_size = 32

max_address_list_size = 100

username_availability_check_response_size = 1024 ** 1 * 16 # THIS NEEDS TO BE TRIMMED
signup_response_size = 1024 ** 1 * 16


def code(n):
	return (n).to_bytes(2, byteorder='little')


decryption_failure_code = code(1)

login_step_1_code = code(2)

login_step_2_code = code(3)

time_limit_exceeded_code = code(4)

username_not_found_code = code(5)

username_found_code = code(6)

update_mailbox_code = code(7)

delete_email_code = code(8)

shred_mailbox_code = code(9)

close_account_code = code(10)

logout_code = code(11)

logout_successful_code = code(12)

logout_failed_code = code(13)

get_public_keys = code(14)

signup_code = code(15)

username_availability_check_code = code(16)

no_changes_in_mailbox = code(17)

invalid_username_code = code(18)

signup_successful_code = code(19)

invalid_signup_credentials = code(20)

okay_code = code(21)


print("\nLoading modules...\n")

with open("./libraries/backend.py") as backend_module:
	cmd = backend_module.read()
exec(cmd)

print("Backend loaded...")

if isfile("./libraries/db"):
	print("Database loaded...")
else:
	print("Database MISSING!\nExiting...")
	exit()

with open("./libraries/database_manager.py") as database_manager_module:
	cmd = database_manager_module.read()
exec(cmd)

print("Database manager loaded...")

with open("./libraries/frontend.py") as frontend_module:
	cmd = frontend_module.read()
exec(cmd)

print("Frontend loaded...")

with open("./libraries/network_manager.py") as network_manager_module:
	cmd = network_manager_module.read()
exec(cmd)

print("Network manager loaded...")

with open("./libraries/main.py") as main_module:
	cmd = main_module.read()
exec(cmd)

del cmd
