import socket
import cv2
import numpy
import threading

def recv_size(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def recv_all(sock, count):
    buf = b''
    while count > 1024:
        newbuf = sock.recv(1024)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)

    newbuf = sock.recv(count)
    buf += newbuf
    
    #buf = sock.recv(count)
    print("recv")
    print(len(buf))
    return buf

cap = cv2.VideoCapture("/dev/video0")
#ret, frame = cap.read()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address_server = ('127.0.0.1', 9587)
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
ret, frame = cap.read()

while ret:
    framebuffer.append(frame)

    if len(framebuffer) > FRAME_BUFFER_SIZE:
        cv2.imshow('process', framebuffer[0])
        displaybuffer.append(framebuffer[0])
        transferbuffer.append(framebuffer[0])
        framebuffer.pop(0)

    if len(displaybuffer) > DISPLAY_BUFFER_SIZE:
        cv2.imshow('display', displaybuffer.pop(0))

    if len(transferbuffer) > TRANSFER_BUFFER_SIZE:
        result, imgencode = cv2.imencode('.jpg', transferbuffer.pop(0))
        transfer_data = numpy.array(imgencode)
        string_transfer_data = transfer_data.tostring()
        
        transfer_len = str(len(string_transfer_data))
        print("transfer: " + transfer_len)
        sock.send(transfer_len.rjust(16).encode())
        sock.send(string_transfer_data)

        # Get video back
        print("Waiting size")
        receive_length = recv_size(sock, 16)
        length = int(receive_length.decode())

        print("Waiting image")
        stringData = recv_all(sock, length)
        data = numpy.fromstring(stringData, numpy.uint8)
        decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)
        cv2.imshow("client", decimg)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    ret, frame = cap.read()
    
