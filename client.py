import socket
import argparse
import sys
import threading

def join_chatroom(host, port, username, passcode):
    # Create socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Send authentication information to the server
    auth_info = f"{username},{passcode}"
    client_socket.sendall(auth_info.encode('utf-8'))

    # Receive server's response
    response = client_socket.recv(1024).decode('utf-8')
    if "Incorrect passcode" in response:
        print(response)
        sys.stdout.flush()
        sys.exit(1)
    else:
        print(response)
        sys.stdout.flush()

    # Start a listening thread for server messages
    threading.Thread(target=listen_to_server, args=(client_socket,)).start()

    # Main loop to send messages
    while True:
        message = input()
        if message == ":Exit":
            client_socket.sendall(message.encode('utf-8'))
            break
        client_socket.sendall(message.encode('utf-8'))

def listen_to_server(client_socket):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            print("Disconnected from the server.")
            sys.stdout.flush()
            sys.exit(0)
        print(message)
        sys.stdout.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Room Client")
    parser.add_argument('-join', action='store_true')
    parser.add_argument('-host', type=str, required=True)
    parser.add_argument('-port', type=int, required=True)
    parser.add_argument('-username', type=str, required=True)
    parser.add_argument('-passcode', type=str, required=True)

    args = parser.parse_args()

    if args.join:
        join_chatroom(args.host, args.port, args.username, args.passcode)
