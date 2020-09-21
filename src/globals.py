from os.path import isfile
from sys import exit
from hmac import compare_digest # IMPLEMENT THIS !!!
from pathlib import Path


def code(n):
	return (n).to_bytes(2, byteorder='little')


SIGNATURE_DENOTER = b'\x00' #10101010

HASH_DENOTER = b'\xff'     #01010101

LOGGGED_IN = False

USERNAME = ''

PASSWORD = ''

SERVER = "server"

SERVER_IP = "127.0.0.1"

SERVER_PORT = 9000

CCR_FOLDER = ".ccr/"

USER_HOME = str(Path.home())+'/'

VERSION = b'\x00\x00'

RANDOM_NAME_LENGTH = 16 # characters in hex

NONCE_SIZE = 32

HASH_SIZE = 32

# UNIX timestamps
TIMESTAMP_SIZE = 4

MAX_ALLOWABLE_TIME_DELTA = 60 # seconds. a proper value needs to set according to network requirements

MAX_USERNAME_SIZE = 64

MESSAGE_ID_SIZE = 2

REQUEST_CODE_SIZE = 2

RESPONSE_CODE_SIZE = 2

ROLLING_ID_SIZE = 8

ROLLING_AUTHENTICATION_TOKEN_SIZE = 32

MAX_ADDRESS_LIST_SIZE = 100

USERNAME_AVAILABILITY_CHECK_RESPONSE_SIZE = 1024 ** 1 * 16 # THIS NEEDS TO BE TRIMMED
SIGNUP_RESPONSE_SIZE = 1024 ** 1 * 16


# REQUEST/RESPONSE CODES

DECRYPTION_FAILURE = code(1)

LOGIN_STEP_1 = code(2)

LOGIN_STEP_2 = code(3)

TIME_LIMIT_EXCEEDED = code(4)

USERNAME_NOT_FOUND = code(5)

USERNAME_FOUND = code(6)

UPDATE_MAILBOX = code(7)

DELETE_EMAIL = code(8)

SHRED_MAILBOX = code(9)

CLOSE_ACCOUNT = code(10)

LOGOUT = code(11)

LOGOUT_SUCCESSFUL = code(12)

LOGOUT_FAILED = code(13)

GET_PUBLIC_KEYS = code(14)

SIGNUP = code(15)

USERNAME_AVAILABILITY_CHECK = code(16)

NO_CHANGES_IN_MAILBOX = code(17)

INVALID_USERNAME = code(18)

SIGNUP_SUCCESSFUL = code(19)

INVALID_SIGNUP_CREDENTIALS = code(20)

OKAY = code(21)