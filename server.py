import socket
import cv2
import numpy
import time
import threading
import transfer

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ('127.0.0.1', 9999)
s.bind(address) 
s.listen(True) 
print ('Waiting for images...')
conn, addr = s.accept()

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


receive_lock = threading.Lock()
transfer_lock = threading.Lock()

sendFrame(transfer_lock, "test").start()
recvFrame(receive_lock, "test").start()

while True:
    if len(receiverbuffer) > 0:
        receive_lock.acquire()
        decimg = receiverbuffer.pop(0)
        receive_lock.release()
        cv2.imshow('SERVER', decimg)

        # Send Back
        transfer_lock.acquire()
        transferbuffer.append(decimg)
        transfer_lock.release()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

s.close()
cv2.destroyAllWindows()
