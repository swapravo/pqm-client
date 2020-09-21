from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from sys import byteorder


import src.globals


def close():
	connection.shutdown(SHUT_RDWR)
	connection.close()


def connect():
	connection = socket(AF_INET, SOCK_STREAM)
	try:
		connection.connect((src.globals.SERVER_IP, src.globals.SERVER_PORT))
		return connection
	except:
		print("Network error...")
		return 1


def recieve(max_payload_size):

	if max_payload_size == 0:
		return b''

	payload_size = int.from_bytes(connection.recv(4), byteorder='little')
	if payload_size > max_payload_size:
		close()
		return b''

	data = bytearray(payload_size)
	pos = 0
	print("payload_size", payload_size)
	total_recieved = 0
	buffer_size = 4096

	while pos < payload_size:
		# insert try catch here in case it looses connectivity
		# insert a timeout here
		chunk = connection.recv(buffer_size)
		chunk_size = len(chunk)
		total_recieved += chunk_size

		data[pos:pos+chunk_size] = chunk
		pos += chunk_size

		if total_recieved == payload_size:
			return data


def send(data):
	try:
		connection.send(data)
	except:
		print("Network ERROR!")
		return 1
		# press xxx to retry


connection = connect()
if connection == 1:
	input("Network Error!")
	# HANDLE THIS SOMEHOW