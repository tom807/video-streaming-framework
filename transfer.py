import socket
import cv2
import numpy

def recv_size(sock, size):
    buf = sock.recv(size)
    return buf

def recv_frame(sock, size):
    buf = b''
    while size > 1024:
        newbuf = sock.recv(1024)
        if not newbuf: return None
        buf += newbuf
        size -= len(newbuf)
    newbuf = sock.recv(size)
    buf += newbuf
    return buf

def trans_size(sock, size):
    transfer_len = str(size)
    sock.send(transfer_len.rjust(16).encode())

# Transfer jpeg
def trans_frame(sock, frame):
    sock.send(frame)

# Convert cv2 frame to jpeg
def convert2jpg(frame):
    result, imgencode = cv2.imencode('.jpg', frame)
    transfer_data = numpy.array(imgencode)
    return transfer_data.tostring()

# Convert jpeg to cv2 frame
def convert2frame(jpg):
    data = numpy.fromstring(jpg, numpy.uint8)
    decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return decimg
