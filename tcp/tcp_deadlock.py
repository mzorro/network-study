# -*- coding:utf-8 -*-
import sys,socket

HOST = '127.0.0.1'
PORT = 2000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if len(sys.argv)==2 and sys.argv[1:]==['server']:
    s.bind((HOST,PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(1)
    while True:
        print 'Listening at:', s.getsockname()
        sock, addr = s.accept()
        n = 0
        while True:
            data = sock.recv(1024)
            if not data:
                break
            print 'Received: %d bytes of data from:' % len(data), sock.getpeername()
            sock.sendall(data.upper())
            n += len(data)
            print 'Processed %d bytes of data so far.' % n
        print
        sock.close()
        print 'Completed processing...'
        print 'Socket closed.'

elif len(sys.argv)==3 and sys.argv[1]=='client' and sys.argv[2].isdigit():
    bytes = (int(sys.argv[2]) + 15) // 16 * 16 # round up to times of 16
    print 'Sending %d bytes of data in chunks of 16 bytes' % bytes
    message = 'come and fuck me'
    s.connect((HOST,PORT))

    sent = 0
    while sent < bytes:
        s.sendall(message)
        sent += len(message)
        print 'Sent %d bytes of data so far.' % sent

    print
    s.shutdown(socket.SHUT_WR)

    print 'Receiving all the data the server sends back...'

    received = 0
    while True:
        data = s.recv(1024)
        if not received:
            print 'The first data received is %d bytes.' % len(data)
        received += len(data)
        if not data:
            break
        print 'Received: %d bytes of data so far.' % received

    s.close()

else:
    print >>sys.stderr, 'usage: tcp_deadlock.py server | client <bytes>'
    
        

            
