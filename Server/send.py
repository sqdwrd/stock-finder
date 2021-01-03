from socket import *
import configparser


def connect_and_send(text: str, port: int):
    before_i = 0
    config = configparser.ConfigParser()
    config_file = open('config.ini')
    config.read_file(config_file)
    config_file.close()
    datafile = open('stock.json', 'r')
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(10)
    client_socket, addr = server_socket.accept()
    text = text.encode('utf-8')
    if len(text)/1024 != int(len(text)/1024):
        repeat_range = int(len(text) / 1024) + 1
    else:
        repeat_range = int(len(text) / 1024) + 1
    for i in range(repeat_range):
        client_socket.send(text[1024 * repeat_range: (1024 * repeat_range) + 1])
