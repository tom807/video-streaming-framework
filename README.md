# video-streaming-framework

## Introduction

This is course project from **National Taiwan University GPU Programming Spring 2018**. The client program will tansfer the videos frames captured by web camera to the server program, and you can do anything what you like to do on these frames in the server program, then the framework will transfer these processed frames back to client program and display.

## Prerequisites

* Install the opencv2 and numpy

  ```shell=
  $ pip3 install --user numpy opencv-python
  ```

## Launch the service

* Launch the server program first

  ```shell
  $ python3 server.py -ip <ip_address> -port <port_number>
  ```

* Then launch the client program

  ```shell
  $ python3 client.py -ip <ip_address> -port <port_number>
  ```

* It is expected to see the following result, while the server doesn't do extra processing on video frames at this time

  ![](https://i.imgur.com/JEgXHiD.png)

## Where to do image processing

You can do extra processing on these frames in the `server.py`

```python
while True:
    if len(receiverbuffer) > 0:
        receive_lock.acquire()
        decimg = receiverbuffer.pop(0)
        receive_lock.release()

        # You can do extra processing on these frames here
        # then append these processed frames into transferbuffer
        # decimg = process(decimg)

        # Send Back
        transfer_lock.acquire()
        transferbuffer.append(decimg)
        transfer_lock.release()
```
## Licensing

`video-streaming-framework` is freely redistributable under the MIT License. Use of this source code is governed by a MIT-style license that can be found in the `LICENSE` file.
