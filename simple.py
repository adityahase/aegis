import socket


SERVER_ADDRESS = (HOST, PORT) = "", 9300
REQUEST_QUEUE_SIZE = 2048


FORWARD_ADDRESS = (FORWARD_HOST, FORWARD_PORT) = "127.0.0.1", 1500

HTTP_REPONSE = b"""\
HTTP/1.1 200 OK

It Works!
"""


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print("Received Request ...")
    print(request.decode())

    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward_socket.connect(FORWARD_ADDRESS)

    print(f"Forwarding Request to ... {FORWARD_HOST}:{FORWARD_PORT}")
    forward_socket.sendall(request)
    response = forward_socket.recv(1024)
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
