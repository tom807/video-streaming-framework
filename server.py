import socket
import cv2
import numpy
import time
import transfer

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ('127.0.0.1', 9997)
s.bind(address) 
s.listen(True) 
print ('Waiting for images...')
conn, addr = s.accept()

while True:
    print("Waiting Client size")
    receive_length = transfer.recv_size(conn, 16)
    length = int(receive_length.decode())
    print("Receive: " + str(length))

    print("Waiting Client image")
    stringData = transfer.recv_frame(conn, length)
    print('Image recieved successfully!')

    # Decode and display
    decimg = transfer.convert2frame(stringData)
    cv2.imshow('SERVER', decimg)

    # Send Back
    string_transfer_data = transfer.convert2jpg(decimg)
 
    print("Send size to Client")
    transfer.trans_size(conn, len(string_transfer_data))
    print("Sent: " + str(len(string_transfer_data)))

    print("Send image to Client")
    transfer.trans_frame(conn, string_transfer_data)
    #conn.send(string_transfer_data)
    print("Image Sent!")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

s.close()
cv2.destroyAllWindows()
