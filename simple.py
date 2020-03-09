import socket


SERVER_ADDRESS = (HOST, PORT) = "", 9300
REQUEST_QUEUE_SIZE = 2048


FORWARD_ADDRESS = (FORWARD_HOST, FORWARD_PORT) = "127.0.0.1", 1500

HTTP_REPONSE = b"""\
HTTP/1.1 200 OK

It Works!
"""


def recieve(connection):
    ## Socket library can't provide the counterpart of sendall()
    ## For our purpose this should serve as a reasonable function
    data = []
    try:
        while True:
            received = connection.recv(1024)
            if received:
                data.append(received)
            else:
                ## This block will only be executed when socket is in 
                ## blocking mode. If recv() returns with b"" then the 
                ## connection is closed and we will never recieve more data.
                ## This is useful while receiving reponse from application
                ## application must call socket.shutdown() or socket.close()
                ## for recv() to return b"".
                break
    except socket.error:
        ## When socket is in nonlocking mode, if no more data can be read then 
        ## socket.recv() will throw socket.error. 
        ## Consider this as the end of message
        pass

    return b"".join(data)


def handle_request(client_connection):
    # Put this socket in nonblocking mode
    # Now socket.recv() is expected to raise socket.error if there is nothing to receive
    # The side effect is that we don't have to decode the Content-Length header and wait till the entire message is recieved
    # CAUTION: This will only work if used after a Bufferring Proxy e.g. NGINX or Waitress
    client_connection.setblocking(0)
    request = recieve(client_connection)

    print("Received Request ...")
    print(request.decode())

    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward_socket.connect(FORWARD_ADDRESS)

    print(f"Forwarding Request to ... {FORWARD_HOST}:{FORWARD_PORT}")
    forward_socket.sendall(request)
    response = recieve(forward_socket)
    print(f"Received response ... ")
    print(response.decode())

    client_connection.sendall(response)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print("Serving HTTP on port {port} ...".format(port=PORT))

    while True:
        client_connection, client_address = listen_socket.accept()
        handle_request(client_connection)
        client_connection.close()


if __name__ == "__main__":
    serve_forever()
