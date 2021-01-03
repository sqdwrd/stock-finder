from socket import *

host = '127.0.0.1'
port = 51299
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((host, port))

while True:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((host, port))
    txt = clientSocket.recv(1024)
    if txt:
        print(txt)
