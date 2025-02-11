# CP372 Assignment 1
# Anubhav Pandey - 210725910
# Inam Ul Haque - 201844530

import socket # Import socket TCP functinality 
import os

# Server Connection Details
S_HOST = '127.0.0.1'
S_PORT = 11000
DOWNLOAD_REPO = "downloads"  # Folder where downloaded files are saved

# Ensure the download folder exists
if not os.path.exists(DOWNLOAD_REPO):
    os.makedirs(DOWNLOAD_REPO)

# Initiliaze client and connect to server function
def init_client():
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #INET is for IPv4 and SOCK_STREAM is for TCP
    c_socket.connect((S_HOST, S_PORT)) # if server not listening, connection will fail

    # Recieve name from server
    c_name = c_socket.recv(1024).decode() # decode from bytes to string
    if c_name == "Server is full":
        print(f"Server is full. Please try later.")
        exit()
    else:
        print(f"Connected as {c_name}") # log client name 

    # Loop to interact with server until 'exit'
    while True:
        message = input(f"{c_name} => ")  # Prompt user
        # if client exits 
        if message.lower() == "exit": # convert to lowercase
            c_socket.send(message.encode())
            print("Disconnecting from server...")
            break
        # if client requests list, recieves from server and prints
        elif message.lower() == "list":
            c_socket.send(message.encode())
            file_list = c_socket.recv(1024).decode() # recieve list in byte chunks
            print("Available files:\n" + file_list) # log file list to user
        # if client requests download, sends to server and recieves file found/missing 
        elif message.startswith("download "):
            c_socket.send(message.encode())
            response = c_socket.recv(1024).decode()
            # if file is found then creates path to download file to download based on file name
            if response.strip() == "File Found":
                #Send a READY signal to the server
                c_socket.send("READY".encode())
                file_name = message.split(" ", 1)[1] # extracts proper filename 
                file_path = os.path.join(DOWNLOAD_REPO, file_name)
                # opens new file in write binary mode to write chunks recieved from server
                with open(file_path, "wb") as file:
                    while True: #Loop through all chunks
                        data = c_socket.recv(1024)
                        # Check if the EOF marker is in the received data
                        if b"<<EOF>>" in data:
                            eof_index = data.find(b"<<EOF>>")
                            file.write(data[:eof_index])
                            break
                        elif not data: #if data is empty, server is finished sending file or connection ended
                            break
                        file.write(data) # writes recieved message into local file
                print(f"File '{file_name}' downloaded successfully.")
            else:
                print(f"File not found on the server.")
        else: # any other message, should be echo'd with ack
            c_socket.send(message.encode()) # send user message to server
            response = c_socket.recv(1024).decode() 
            print(f"Server: {response}") # log response 
    # Client exits loop, types 'exit'
    c_socket.close() # close socket

# python idiom to run init_client
if __name__ == "__main__":
    init_client()