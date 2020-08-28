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
from datetime import datetime, timezone
from string import printable
from re import search
from getpass import getpass
from time import sleep

server_ip = "192.168.43.109"
server_port = 9000

def send(data, number_of_bytes):

	network = socket(AF_INET, SOCK_STREAM)
	network.connect((server_ip, server_port))

	try:
		network.send(data)
		network.shutdown(SHUT_WR)	# signal to the server that it has no more data to send
		print("SET A TIMEOUT HERE!")
		response = network.recv(number_of_bytes)
		network.close()

	except Exception as err:
		print("Network error: ", err)
		return 1

	return response

send(urandom(64), 64)
