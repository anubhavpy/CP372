# CP372 Assignment 1
# Anubhav Pandey - 210725910
# Inam Ul Haque - 201844530


import socket # Allows us to create TCP connection
import threading # Allows us to handle multiple clients at same time
import os # Allows interaction with OS for listing files etc.
from datetime import datetime # Allows us to record time when client connects/disconnects

# Configuring Server
HOST = '127.0.0.1' # IP address for localhost, server only accessible from same computer 
PORT = 11000 # Port number that server listens to, abritrary unused port 
CLIENT_MAX = 3 # Maximum amount of clients connected to server at the same time, assignment specified 
FILE_REPO = "server_files" # Folder for files for listing/send to client, per bonus 

# Check File Repository Existence 
if not os.path.exists(FILE_REPO):
    os.makedirs(FILE_REPO) # Creates directory (repo) if not found 

# Initialize Client 
clients = {} # Dictionary of form: {client_name: (ip_address, connect_time, disconnect_time)}

# Function to handle client communication 
def client_com(c_socket, c_address, c_name): # Requires client socket, address, and name
    # Output for connected client 
    ## Unneccesary: print(f"{c_name} connected from {c_address}")
    # Store client details based on connection time and ip/port
    connect_time = datetime.now().strftime('%Y-%M-%D %H:%m:%S') # Collects current time and formats in Y/M/D and H/M/S format
    # Store in clients dictionary 
    clients[c_name] = (c_address, connect_time, None) #Stores client address and connect time, no disconnect time yet
    # Try/Except Block to listen to client messages
    try:
        while True: # Loop continuously
            c_message = c_socket.recv(1024).decode() # converts client data in socket to string
            if not c_message: # if client sends empty message
                break
            # Log client message to console
            print(f"{c_name} sent: {c_message}")
            # Checks message and executes functions depending on message content
            if c_message.lower() == "exit":
                disconnect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # sets disconnect time to when exit message recieved
                # Adds disconnect time to client dictionary 
                clients[c_name] = (c_address, connect_time, disconnect_time)
                # Log client disconnect to console
                print(f"{c_name} disconnected at {disconnect_time}")
                break
            elif c_message.lower() == "status":
                status_message = "Active Clients:\n"
                for name, data in clients.items():
                    status_message += f"{name} - Connected from {data[0]} at {data[1]}\n"
                c_socket.send(status_message.encode())  # Send the formatted message
            elif c_message.lower() == "list":
                # Send list of files in repo to client 
                files = os.listdir(FILE_REPO)
                file_list = "\n".join(files) if files else "No files available."
                c_socket.send(file_list.encode()) # convert list to bytes then send to client 
            elif c_message.startswith("download "):
                # extract specific file by first space and use second word as filename for download
                file_name = c_message.split(" ", 1)[1]
                file_path = os.path.join(FILE_REPO, file_name) # Creates path to requested file on server 
                # checks if requested file exists
                if os.path.exists(file_path):
                    c_socket.send("File Found".encode()) # Send client message that requested file found
                    # Wait for the client to send a READY signal
                    ready = c_socket.recv(1024).decode()
                    if ready.strip() == "READY":
                        with open(file_path, "rb") as file: # Opens file in read binary mode, may be txt file or other
                            while chunk := file.read(1024): # read file in byte chunks
                                c_socket.send(chunk) #send to client 
                        c_socket.send("<<EOF>>".encode())
                        print(f"Sent file '{file_name}' to {c_name}")
                    else:
                        print(f"{c_name} did not send READY signal. Aborting file transfer.")
                else:
                    # Tell client file doesn't exist
                    c_socket.send("File Not Found".encode())
            else: # All other client messages should be relayed with ACK
                # echo message
                response = f"{c_message} ACK"
                # send response
                try:
                    c_socket.send(response.encode())
                except BrokenPipeError:
                    print(f"[{c_name}] disconnected before receiving ACK.")
    except Exception as e: # Any errors in message or response use error handling
        print(f"Error for {c_name}: {e}")
    finally:
        # if error or normal exit, close socket connection and remove client from dictionary
        c_socket.close()
        del clients[c_name]
        print(f"{c_name} connection closed.")

# Function to initiate server and listen for clients
def init_server():
    # Create socket and TCP connection
    s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind socket to host and port 
    s_socket.bind((HOST, PORT))
    # Put socket in listening mode for up to 3 clients
    s_socket.listen(CLIENT_MAX)

    # Log server running
    print(f"Server started on {HOST}:{PORT}, allowing up to {CLIENT_MAX} clients.")

    client_total = 1 # Track number of clients 

    # Handle connections 
    while True:
        c_socket, c_address = s_socket.accept() # When new client tries to connect, returns tuple 
        if len(clients) < CLIENT_MAX: # Ensure amount of clients less than max
            c_name = f"Client{client_total:02d}" # Assign name to client with 2 digit format
            c_socket.send(c_name.encode()) # Inform client of their name 
            print(f"{c_name} assigned and connected from {c_address}")
            # create thread to run client_com and passes parameters c_socket/address/name
            threading.Thread(target=client_com, args=(c_socket, c_address, c_name)).start()
            client_total += 1 # increment counter for next client name 
        else: # if client list full
            print(f"Server is full. Cannot accept new connections from {c_address}.")
            c_socket.send("Server is full".encode())  # Send message
            c_socket.close()  # Close connection

# Python idiom function to start server when run 
if __name__ == "__main__":
    init_server()
