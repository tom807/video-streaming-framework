import socket
import cv2
import numpy
import time

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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ('127.0.0.1', 9587)
s.bind(address) 
s.listen(True) 
print ('Waiting for images...')
conn, addr = s.accept()

while 1:
    print("Waiting size")
    receive_length = recv_size(conn, 16) 
    length = int(receive_length.decode())
    print(length)
    if 2 > 1:
        print("Waiting image")
        stringData = recv_all(conn, length)
        data = numpy.fromstring(stringData, numpy.uint8)
        decimg=cv2.imdecode(data, cv2.IMREAD_COLOR) 
        cv2.imshow('SERVER', decimg)
        if cv2.waitKey(10) == 27:
            break 
        print('Image recieved successfully!')
        
        # Send Back
        result, imgencode = cv2.imencode('.jpg', decimg)
        transfer_data = numpy.array(imgencode)
        string_transfer_data = transfer_data.tostring()
        transfer_len = str(len(string_transfer_data))
        print("Transfer: " + transfer_len)
        conn.send(transfer_len.rjust(16).encode())
        conn.send(string_transfer_data)

        #conn.send("Server has recieved messages!".encode())
    #if cv2.waitKey(10) == 27:
    #    break 

s.close()
cv2.destroyAllWindows()
