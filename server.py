import random
import select
import socket
import subprocess
import time
from multiprocessing import Process
from queue import Queue

import client

keyDict = {}
SERVER_PORT = 48000
SERVER_IP = 'localhost'
MAX_MSG_LENGTH = 1024
SENDER_IP = "s"
SENDER_PORT = "p"
cmd_command = 'ngrok.exe tcp 48000'


def join(roompass, ng_ip, port, client_socket):
    key = hash(roompass)
    if key in keyDict:
        establish_connection(key, ng_ip, port, client_socket)
        return
    keyDict[key] = (ng_ip+port, client_socket)


def establish_connection(key, ng_ip, port, client_socket):
    if ng_ip == SENDER_IP:
        client_socket.send((str(len((keyDict[key][0]))).zfill(10).encode()))
        client_socket.send(keyDict[key][0].encode())
        return
    keyDict[key][1].send(str(len((ng_ip+port))).zfill(10).encode())
    keyDict[key][1].send((ng_ip+port).encode())


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    return server_socket


def read_msg(current_socket):
    data_len = current_socket.recv(7).decode()
    data = current_socket.recv(int(data_len)).decode()
    return data


def noam():
    popen = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, universal_newlines=True)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd_command)


def main():
    server_socket = start_server()
    messages_to_send = []
    client_sockets = []
    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                client_sockets.append(connection)
            else:
                data_len = current_socket.recv(10).decode()
                if data_len != '':
                    data = current_socket.recv(int(data_len)).decode()
                    if data != "":
                        data = data.split("\n")
                        join(data[0], data[1], data[2], current_socket)
        for message in messages_to_send:
            current_socket, data = message
            if current_socket in wlist:
                current_socket.send(data.encode())
                messages_to_send.remove(message)


if __name__ == "__main__":
    main()
