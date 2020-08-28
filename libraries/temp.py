
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


