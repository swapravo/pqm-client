from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, SOL_SOCKET, SO_REUSEADDR

import src.globals


def close():
	print("Closing connection")
	connection.shutdown(SHUT_RDWR)
	connection.close()


def connect():
	connection = socket(AF_INET, SOCK_STREAM)
	connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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

	if payload_size == 0:
		print("Dropping Undersized request!")
		return b''
	elif payload_size > max_payload_size:
		print("Dropping Oversized request!", payload_size, max_payload_size)
		close(connection)
		return b''

	data = bytearray(payload_size)
	pos = 0
	total_recieved = 0
	buffer_size = 4096

	while pos < payload_size:
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
		return 0
	except:
		print("Network Error")
		return 1


connection = connect()
if connection == 1:
	input("Network Error!")
	# HANDLE THIS SOMEHOW
