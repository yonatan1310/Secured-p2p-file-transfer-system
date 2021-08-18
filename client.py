import math
import subprocess
import socket
import os
from multiprocessing import Process, Queue
import time

from google_images_search import GoogleImagesSearch

import enc

SERVER_URL = 'localhost'
cmd_command = 'ngrok.exe tcp 49000 --log "stdout"'
PORT = 48000
NUMBER_OF_BYTES = 40
MAX_LENGTH = 10
BLOCK_SIZE = 1024


def connect_to_server():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER_URL, PORT))
    return my_socket


def send_to_peer(peer_info, password):
    domain = 'localhost'
    port = 49000
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((domain, int(port)))
    file_name = input("enter the name of the file you wish to send:")
    enc.encrypt_file(password, file_name)
    block_cnt = 0
    num_of_blocks = str(math.ceil(os.path.getsize(file_name) / BLOCK_SIZE))
    enc_num_of_blocks = enc.encrypt(password, num_of_blocks)
    my_socket.send(str(len(enc_num_of_blocks)).zfill(10).encode())
    my_socket.send(enc_num_of_blocks)
    with open(file_name, 'rb') as my_file:
        my_socket.send(file_name.zfill(BLOCK_SIZE).encode())
        while block_cnt <= int(num_of_blocks):
            my_socket.send(my_file.read(BLOCK_SIZE))
            block_cnt += 1
    enc.decrypt_file(password, file_name)
    my_socket.close()


def listen_to_peer(password):
    server_socket = socket.socket()
    server_socket.bind(('localhost', 49000))
    server_socket.listen()
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")
    block_cnt = 0
    while True:
        len_num_of_blocks = client_socket.recv(10).decode()
        num_of_blocks = client_socket.recv(int(len_num_of_blocks)).decode()
        try:
            num_of_blocks = enc.decrypt(num_of_blocks.encode(), password)
        except:
            client_socket.close()
        break
    file_name = client_socket.recv(BLOCK_SIZE).decode().lstrip('0')
    time.sleep(5)
    with open("new " + file_name, 'wb') as my_file:
        while block_cnt <= int(num_of_blocks):
            block = client_socket.recv(BLOCK_SIZE)
            my_file.write(block)
            block_cnt += 1
    client_socket.close()
    server_socket.close()
    time.sleep(8)
    enc.decrypt_file(password, "new " + file_name)
    print("new file have been moved to your directory.")


def noam(q):
    print('hi')
    popen = subprocess.Popen(cmd_command, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        q.put(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd_command)


def get_url(q):
    s = ""
    while "url" not in s:
        s = q.get()
    domain_place = s.find('tcp')
    port_place = s.find('.io:') + 4
    domain = s[domain_place:port_place - 1:]
    port = s[port_place:port_place + 5]
    return domain, port


def download_image(query, num):
    search_params = {
        'q': query,
        'num': num,
    }
    gis = GoogleImagesSearch('AIzaSyBT09htpBpPQtuD3GVi_v-N1Q5yZJ3jDkw', '34c782162a803adc6')
    gis.search(search_params=search_params, custom_image_name=query + str(num))
    image = gis.results()[num - 1]
    image.download(os.path.dirname(os.path.abspath(__file__))[2::].replace("\\", "/"))


def get_img_data(filename):
    with open(filename, 'rb') as img:
        img.read(1000)  # the header of every jpg file is the same. after 1000 bytes, there will be differences.
        return img.read(NUMBER_OF_BYTES), img.read(NUMBER_OF_BYTES)


def send_to_server(mysocket, domain, port):
    query = input("please enter a word:")
    num = input("please enter a number:")
    # download_image(query, int(num))
    # room_pass, password = get_img_data(query + num + ".jpg")
    room_pass, password = get_img_data("banana1.jpg")
    data = str(room_pass) + "\n" + domain + "\n" + str(port) + "\n"
    mysocket.send(str(len(data)).zfill(10).encode())
    mysocket.send(data.encode())
    # os.remove(query + str(num) + ".jpg")
    return password


def main():
    is_receiver = input("do you want to send or receive a file?") == "receive"
    if is_receiver:
        domain, port = 'localhost', 49000
    else:
        domain, port = "s", "s"
    mysocket = connect_to_server()
    password = send_to_server(mysocket, domain, port)
    if is_receiver:
        mysocket.close()
        listen_to_peer(password)
    else:
        peer_info_len = mysocket.recv(10).decode()
        peer_info = mysocket.recv(int(peer_info_len)).decode()
        mysocket.close()
        send_to_peer(peer_info, password)


if __name__ == "__main__":
    main()
