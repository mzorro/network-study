# -*- coding:utf-8 -*-
import random, socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

MAX = 65535
PORT = 2000

if 2<=len(sys.argv)<=3 and sys.argv[1] == 'server':
    hostname = sys.argv[2] if len(sys.argv)==3 else ''
    s.bind((hostname, PORT))
    print 'Listening on:', s.getsockname()
    while True:
        data, address = s.recvfrom(MAX)
        if random.randint(0,2):
            s.sendto('You have sent me %d bytes of data.' % len(data), address)
        else:
            print 'Pretending to drop packet from:', address

elif len(sys.argv)==3 and sys.argv[1] == 'client':
    hostname = sys.argv[2]
    s.connect((hostname, PORT))
    print 'Client socket name:', s.getsockname()
    delay = 1.0
    while True:
        s.send('This is a message!')
        s.settimeout(delay)
        print 'Wating up to %.1f seconds for a reply...' % delay
        try:
            data = s.recv(MAX)
        except socket.timeout:
            delay *= 2
            if delay > 20.0:
                raise RuntimeError('I think the server is down.')
        except:
            raise # raise other errors
        else:
            print 'Receved reply from the server.'
            break # we can assure that our msg has reached the server.
else:
    print >>sys.stderr, 'useag: udp_remote.py server [ <interface> ]'
    print >>sys.stderr, '   or: udp_remote.py client <hostname>'
        
