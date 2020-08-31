from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
from os import urandom, listdir
from os.path import isfile
from sys import byteorder, exit
from hashlib import sha512, blake2b
from whirlpool import new as whirlpool
from pathlib import Path
from subprocess import Popen, PIPE
from sh import mkdir, mount, shred, umount, rm, touch
from sh.contrib import sudo
from time import time
from string import printable
from re import search
from getpass import getpass
from time import sleep


# global variables

asymmetric_byte = b'\xaa' #10101010

symmetric_byte = b'U'     #01010101

header_byte_size = 1

loggged_in = False

username = ''

password = ''

server = "server"

server_ip = "127.0.0.1"

server_port = 9000

ccr_folder = ".ccr/"

user_home = str(Path.home())+'/'

version = b'\x00\x00'

payload_size = 0

payload_size_size = 4

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

max_encryption_public_key_size = 2 # upto 4209 + max_username_size + int(log10(number_of_characters_in_username))) + 1

max_signature_public_key_size = 2

rolling_public_key_size = max_encryption_public_key_size + random_name_length

key_fingerprint_size = 64

max_address_list_size = 2

bcc_address_list_size = 1

cc_address_list_size = 1

username_availability_check_request_size = 1024 ** 1 * 13 # THIS NEEDS TO BE TRIMMED # 1 + nonce_size + max_username_size + request_size + rolling_public_key_size + hash_size

username_availability_request_response_size = 1024 ** 1 * 16 # THIS NEEDS TO BE TRIMMED

max_signup_request_size = 1024 ** 1 * 20 #1 + nonce_size + max_username_size + request_code_size + max_encryption_public_key_size + max_signature_public_key_size

max_signup_response_size = 1024 ** 1 * 16 # THIS NEEDS TO BE TRIMMED


def code(n):
	return (n).to_bytes(2, byteorder='little')


print("THESE CODES ARE TEMPORARY!!!")


not_found_code = code(1)

forbidden_code = code(2)

failure_code = code(3)

decryption_failure_code = code(4)

login_step_1_code = code(5)

login_step_2_code = code(6)

time_limit_exceeded_code = code(7)

username_not_found_code = code(8)

username_found_code = code(9)

nonce_verification_failed_code = code(10)

email_upcoming_code = code(11)

is_an_email_code = code(12)

update_mailbox_code = code(13)

delete_message_code = code(14)

shred_mailbox_code = code(15)

close_account_code = code(16)

close_account_successful_code = code(17)

close_account_failed = code(18)

logout_code = code(19)

logout_successful_code = code(20)

logout_failed_code = code(21)

download_public_keys = code(22)

fetch_public_keys_code = code(23)

signup_code = code(24)

username_availability_check_code = code(25)

no_changes_in_mailbox = code(26)

invalid_username_code = code(27)


print("\nLoading modules...\n")

with open("./libraries/backend.py") as module:
	cmd = module.read()
exec(cmd)

print("Backend loaded...")

with open("./libraries/frontend.py") as module:
	cmd = module.read()
exec(cmd)

print("Frontend loaded...")

with open("./libraries/network_manager.py") as module:
	cmd = module.read()
exec(cmd)

print("Network manager loaded...")

with open("./libraries/main.py") as module:
	cmd = module.read()
exec(cmd)

del cmd
