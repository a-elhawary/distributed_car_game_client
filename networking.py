import socket
import threading
import random
from datetime import datetime

# Game works with a simple protocol on top of UDP
# data packets -> packets that carry game info e.g. position/chat message
# Anyone packets -> broadcast for finding people on LAN
# Handshake packets -> reply showing computers in LAN

isRunning = True

reciever_port = 8989
send_to = []

send_buffer = []
recieve_buffer = []

my_id = 0


def send(data):
    send_buffer.append("DATA " + data)


def sender():
    global send_buffer
    global isRunning
    global my_id
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    random.seed()
    my_id = str(random.randint(1,1000))
    print(my_id)
    send_buffer.append("ANYONE " + my_id)
    while isRunning:
        if len(send_buffer) > 0:
            msg = send_buffer.pop(0)
            if msg.split(" ")[0] == "ANYONE":
                send_sock.sendto(msg.encode(), ("255.255.255.255", reciever_port))
            elif len(send_to) > 0:
                for node in send_to:
                    send_sock.sendto(msg.encode(), (node, reciever_port))


def listener():
    global isRunning
    global recieve_buffer
    global my_id
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", reciever_port))
    while isRunning:
        data, addr = s.recvfrom(1024)
        ip = addr[0]
        msg = data.decode("utf8")
        header = msg.split(" ")[0]
        args = msg[len(header)+1:]
        print(data, addr)
        if header == "DATA":
            recieve_buffer.append(args)
        elif header == "HANDSHAKE" and ip not in send_to:
            print(ip, " Added")
            send_to.append(ip)
        elif header == "ANYONE" and args != my_id:
            if ip not in send_to:
                print(ip, " Added")
                send_to.append(ip)
            sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sendSock.sendto(b'HANDSHAKE ', (ip, reciever_port))
            sendSock.close()


def start_threads():
    t1 = threading.Thread(target=sender)
    t2 = threading.Thread(target=listener)

    t1.start()
    t2.start()


def stop_threads():
    isRunning = False


def main():
    start_threads()
    while True:
        data = input("enter msg: ").encode()
        send_buffer.append(data)


if __name__ == "__main__":
    main()
