import socket
import cv2
import numpy
import threading
import transfer
from argparse import ArgumentParser

framebuffer = []
displaybuffer = []
transferbuffer = []
receiverbuffer = []

#VIDEO_SOURCE = "/dev/video0"
VIDEO_SOURCE = 0
FRAME_BUFFER_SIZE = 125
DISPLAY_BUFFER_SIZE = 10
TRANSFER_BUFFER_SIZE = 20
RECEIVER_BUFFER_SIZE = 20

class fetchFrame(threading.Thread):
    def __init__(self, display_lock, transfer_lock, threadName):
        super(fetchFrame, self).__init__(name = threadName)
        self.dlock = display_lock
        self.tlock = transfer_lock

    def run(self):
        while True:
            ret, frame = cap.read()
            framebuffer.append(frame)

            if len(framebuffer) > FRAME_BUFFER_SIZE:
                self.dlock.acquire()
                displaybuffer.append(framebuffer[0])
                self.dlock.release()

                self.tlock.acquire()
                transferbuffer.append(framebuffer[0])
                self.tlock.release()

                framebuffer.pop(0)

class sendFrame(threading.Thread):
    def __init__(self, transfer_lock, threadName):
        super(sendFrame, self).__init__(name = threadName)
        self.tlock = transfer_lock

    def run(self):
        while True:
            if len(transferbuffer) > TRANSFER_BUFFER_SIZE:
                self.tlock.acquire()
                string_transfer_data = transfer.convert2jpg(transferbuffer.pop(0))
                self.tlock.release()

                print("Send size to server")
                transfer.trans_size(sock, len(string_transfer_data))
                print("Sent: " + str(len(string_transfer_data)))

                print("Send image to server")
                transfer.trans_frame(sock, string_transfer_data)
                print("Image Sent!")

class recvFrame(threading.Thread):
    def __init__(self, receive_lock, threadName):
        super(recvFrame, self).__init__(name = threadName)
        self.rlock = receive_lock

    def run(self):
        while True:
            print("Waiting Server size")
            receive_length = transfer.recv_size(sock, 16)
            length = int(receive_length.decode())
            print("Receive: " + str(length))

            print("Waiting Server image")
            stringData = transfer.recv_frame(sock, length)
            print("Image received successfully!")

            decimg = transfer.convert2frame(stringData)

            self.rlock.acquire()
            receiverbuffer.append(decimg)
            self.rlock.release()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-ip", dest = "ip", default = "127.0.0.1")
    parser.add_argument("-port", dest = "port", default = "9527")

    args = parser.parse_args()
    ip_address = args.ip
    port_number = int(args.port)

    cap = cv2.VideoCapture(VIDEO_SOURCE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address_server = (ip_address, port_number)
    sock.connect(address_server)

    display_lock = threading.Lock()
    transfer_lock = threading.Lock()
    receive_lock = threading.Lock()

    fetchFrame(display_lock, transfer_lock, "test").start()
    sendFrame(transfer_lock, "test").start()
    recvFrame(receive_lock, "test").start()

    while True:
        if len(displaybuffer) > DISPLAY_BUFFER_SIZE:
            display_lock.acquire()
            disimg = displaybuffer.pop(0)
            display_lock.release()
            cv2.imshow('display', disimg)

        if len(receiverbuffer) > RECEIVER_BUFFER_SIZE:
            receive_lock.acquire()
            decimg = receiverbuffer.pop(0)
            receive_lock.release()
            cv2.imshow("client", decimg)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    sock.close()
    cv2.destroyAllWindows()
