def connect():
	connection = socket(AF_INET, SOCK_STREAM)
	try:
		connection.connect((server_ip, server_port))
		return connection
	except:
		print("Network error...")
		return 1


def recieve(connection, max_payload_size):

	if max_payload_size == 0:
		return b''

	payload_size = int.from_bytes(connection.recv(4), byteorder='little')
	if payload_size > max_payload_size:
		close(connection)
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


def send(connection, data):
	try:
		connection.send(data)
	except:
		print("Network ERROR!")
		return 1
		# press xxx to retry


connection = connect()

if connection == 1:
	input("Network Error!")



"""
#data = urandom(1024**2 *16)
#send(data)

		i = 0
		while True:
			response = send(request, username_availability_check_response_size)
			if response != 1:
				break
			i += 1
			print("Network Error. Retrying...")
			if i == 3: # Retry thrice before bothering the user
				print("Sending message to the server failed.")
				while True:
					n = input("1. Quit or 2. [Retry]: ")
					if n == 1 or n.lower() == 'quit':
						return
					elif n == '' or n == 2 or n.lower() == 'retry':
						i = 0

#from hashlib import md5
#from socket import socket, AF_INET, SOCK_STREAM, SHUT_WR
#from os import urandom
#server_ip = "192.168.43.109"
#server_port = 9000


def recieve2(connection, data_size):

        fragments = []

        while True:
                chunk = connection.recv(data_size)

                if not chunk: break
                fragments.append(chunk)

        return b''.join(fragments)

def recieve(connection, data_size):

        data = bytearray(data_size)

        pos = 0
        total_recieved = 0
        buffer_size = 4096

        while pos < data_size:
                chunk = connection.recv(buffer_size)
                chunk_size = len(chunk)
                total_recieved += chunk_size

                if not chunk: break

                data[pos:pos+chunk_size] = chunk
                pos += chunk_size

        if pos == data_size:
                return data

        return data[:total_recieved]



"""
