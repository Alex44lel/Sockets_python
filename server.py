import socket
import threading
import argparse
import sys
import datetime


clients = {}  # Dictionary to keep track of connected clients

def handle_client(client_socket, username):
    global clients
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == ":Exit":
                print(f"{username} left the chatroom")
                sys.stdout.flush()
                broadcast(f"{username} left the chatroom", client_socket)
                del clients[username]
                client_socket.close()
                break
            message = parse_message(message)
            print(f"{username}: {message}")
            sys.stdout.flush()
            broadcast(f"{username}: {message}", client_socket)
        except:
            continue

def broadcast(message, client_socket=None):
    global clients
    for user, socket in clients.items():
        if socket != client_socket:  # Don't send back to the sender
            try:
                socket.sendall(message.encode('utf-8'))
            except:
                socket.close()
                del clients[user]

def parse_message(message):
    message = message.replace(":)", "[feeling happy]")
    message = message.replace(":(", "[feeling sad]")
    
    # Handle time-related commands
    if message == ":mytime":
        current_time = datetime.datetime.now()
        return current_time.strftime("%a %b %d %H:%M:%S %Y")
    elif message == ":+1hr":
        current_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        return current_time.strftime("%a %b %d %H:%M:%S %Y")
    
    return message

def start_server(port, passcode):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(10)
    print(f"Server started on port {port}. Accepting connections")
    sys.stdout.flush()
    while True:
        client, addr = server_socket.accept()
        auth_info = client.recv(1024).decode('utf-8')
        username, client_passcode = auth_info.split(',')
        if client_passcode == passcode:
            client.sendall(f"Connected to 127.0.0.1 on port {port}".encode('utf-8'))
            print(f"{username} joined the chatroom")
            sys.stdout.flush()
            clients[username] = client
            broadcast(f"{username} joined the chatroom", client)
            threading.Thread(target=handle_client, args=(client, username)).start()
        else:
            client.sendall("Incorrect passcode".encode('utf-8'))
            client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Room Server")
    parser.add_argument('-start', action='store_true', help="Start server flag")
    parser.add_argument('-port', type=int, required=True, help="Port to listen on")
    parser.add_argument('-passcode', type=str, required=True, help="Passcode for the chatroom")

    args = parser.parse_args()

    if args.start:
        start_server(args.port, args.passcode)
