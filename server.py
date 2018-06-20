import socket
import cv2
import numpy
import time
import threading
import transfer
from argparse import ArgumentParser

receiverbuffer = []
transferbuffer = []

class recvFrame(threading.Thread):
    def __init__(self, receive_lock, threadName):
        super(recvFrame, self).__init__(name = threadName)
        self.rlock = receive_lock

    def run(self):
        while True:
            print("Waiting client size")
            receive_length = transfer.recv_size(conn, 16)
            length = int(receive_length.decode())
            print("Receive: " + str(length))

            print("Waiting client image")
            stringData = transfer.recv_frame(conn, length)
            print("Image received successfully!")

            decimg = transfer.convert2frame(stringData)

            self.rlock.acquire()
            receiverbuffer.append(decimg)
            self.rlock.release()

class sendFrame(threading.Thread):
    def __init__(self, transfer_lock, threadName):
        super(sendFrame, self).__init__(name = threadName)
        self.tlock = transfer_lock

    def run(self):
        while True:
            if len(transferbuffer) > 0:
                self.tlock.acquire()
                string_transfer_data = transfer.convert2jpg(transferbuffer.pop(0))
                self.tlock.release()
 
                print("Send size to client")
                transfer.trans_size(conn, len(string_transfer_data))
                print("Sent: " + str(len(string_transfer_data)))

                print("Send image to client")
                transfer.trans_frame(conn, string_transfer_data)
                print("Image Sent!")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-ip", dest = "ip", default = "127.0.0.1")
    parser.add_argument("-port", dest = "port", default = "9527")

    args = parser.parse_args()
    ip_address = args.ip
    port_number = int(args.port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (ip_address, port_number)
    s.bind(address) 
    s.listen(True) 
    conn, addr = s.accept()

    receive_lock = threading.Lock()
    transfer_lock = threading.Lock()

    sendFrame(transfer_lock, "test").start()
    recvFrame(receive_lock, "test").start()

    while True:
        if len(receiverbuffer) > 0:
            receive_lock.acquire()
            decimg = receiverbuffer.pop(0)
            receive_lock.release()
            # Display the video received on the server ?
            # cv2.imshow('SERVER', decimg)

            # You can do extra processing on these frames here
            # then append these processed frames into transferbuffer
            # decimg = process(decimg)

            # Send Back
            transfer_lock.acquire()
            transferbuffer.append(decimg)
            transfer_lock.release()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    s.close()
    cv2.destroyAllWindows()
