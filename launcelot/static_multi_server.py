import time, launcelot
from threading import Thread
from simple_server import setup_server
from simple_server import server_loop
def make_thread(listen_sock):
    thread = Thread(target=server_loop, args=(listen_sock,))
    thread.daemon = True
    thread.start()
    return thread

listen_sock = setup_server()
threads = []
# start 10 threads to run accpet() on the same listening sock
for i in range(10):
    threads.append(make_thread(listen_sock))

# check every 2 seconds for dead threads, and replace them
while True:
    time.sleep(2)
    for i, t in enumerate(threads):
        if not t.is_alive():
            print t.name(), 'died! starting replacement'
            threads[i] = make_thread(listen_sock)