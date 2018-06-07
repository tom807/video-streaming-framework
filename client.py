import socket
import cv2
import numpy
import threading
import transfer

cap = cv2.VideoCapture("/dev/video0")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address_server = ('127.0.0.1', 9997)
sock.connect(address_server)

framebuffer = []
displaybuffer = []
transferbuffer = []

FRAME_BUFFER_SIZE = 125
DISPLAY_BUFFER_SIZE = 10
TRANSFER_BUFFER_SIZE = 20

class Display(threading.Thread):
    def __init__(self, lock, threadName):
        super(Display, self).__init__(name = threadName)
        self.lock = lock

    def run(self):
        while 2 > 1:
            if len(displaybuffer) > BUFFER_SIZE:
                self.lock.acquire()
                frame = displaybuffer.pop(0)
                self.lock.release()
                #cv2.imshow('display', frame)

'''
lock = threading.Lock()
Display(lock, "display").start()
'''

while True:
    ret, frame = cap.read()
    framebuffer.append(frame)

    if len(framebuffer) > FRAME_BUFFER_SIZE:
        cv2.imshow('process', framebuffer[0])
        displaybuffer.append(framebuffer[0])
        transferbuffer.append(framebuffer[0])
        framebuffer.pop(0)

    if len(displaybuffer) > DISPLAY_BUFFER_SIZE:
        cv2.imshow('display', displaybuffer.pop(0))

    if len(transferbuffer) > TRANSFER_BUFFER_SIZE:
        string_transfer_data = transfer.convert2jpg(transferbuffer.pop(0))
        
        print("Send size to server")
        transfer.trans_size(sock, len(string_transfer_data))
        print("Sent: " + str(len(string_transfer_data)))

        print("Send image to server")
        transfer.trans_frame(sock, string_transfer_data)
        #sock.send(string_transfer_data)
        print("Image Sent!")

        # Get video back
        print("Waiting Server size")
        receive_length = transfer.recv_size(sock, 16)
        length = int(receive_length.decode())
        print("Receive: " + str(length))

        print("Waiting Server image")
        stringData = transfer.recv_frame(sock, length)
        print("Image received successfully!")

        decimg = transfer.convert2frame(stringData)
        cv2.imshow("client", decimg)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

sock.close()
cv2.destroyAllWindows()
