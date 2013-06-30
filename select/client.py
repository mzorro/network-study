import socket

messages = ['This is the messages',
            'It will be sent',
            'in parts']

print 'Connecting to the server'

server_addr = ('127.0.0.1',2000)

socks = []

for i in range(10):
    socks.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))

for s in socks:
    s.connect(server_addr)

for msg in messages:
    # send msg to server from different sockets
    for s in socks:
        print 'Sending:',repr(msg),'To:',s.getpeername()
        s.send(msg)

    # read response on each sockets
    for s in socks:
        data = s.recv(1024)
        print 'Receved:',repr(data),'From',s.getpeername()
        if not data:
            print "Closing socket:",s.getsockname()
            s.close()
