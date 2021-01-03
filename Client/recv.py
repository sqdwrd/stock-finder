from socket import *


def receive_str(addr: str, port: int):
    status = 0
    full_file = ''
    time = 0
    while True:
        try:
            client_sock = socket(AF_INET, SOCK_STREAM)
            client_sock.connect((addr, port))
            txt = client_sock.recv(1024)
            print(txt.decode('utf-8'))
            if txt.decode('utf-8') == 'BoF':
                status = 1
            if txt.decode('utf-8') == 'EoF':
                status = 0
                break
            if status == 1:
                for i in list(txt.decode('utf-8')):
                    full_file.join(i)
        except:
            pass
    print(full_file)
    return full_file
