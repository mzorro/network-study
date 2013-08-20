# -*- coding:utf-8 -*-
import threading, socket
from zchat import *
logger = Logger('client')

def recv_cmd(sock):
    logger('socket %s receiving...' % repr(sock.getsockname()))
    line = ''
    while not line.endswith('\r\n'):
        line += sock.recv(1024)
    return LINE_TO_CMD(line)

def send_cmd(sock, cmd):
    logger('socket %s sending...' % repr(sock.getsockname()))
    line = CMD_TO_LINE(cmd)
    sock.sendall(line)

def connect_to_server():
    sock = socket.socket()
    sock.settimeout(TIMEOUT)
    try:
        sock.connect((HOST, PORT))
    except socket.timeout as e:
        logger.error('client connection time out!')
        logger.error(repr(e))
        return u'网络连接超时！'
    except socket.error as e:
        logger.error(repr(e))
        return u'网络错误！'
    return sock

class Client():

    def __init__(self, app):
        self.app = app
        self.make = RequestMaker()
        self.sock = None
        
    def connect(self):
        result = connect_to_server()
        if isinstance(result, unicode):
            return result
        else:
            self.sock = result
            self.sock.settimeout(TIMEOUT)
            return None
            
    def makeRequest(self, *args):
        cmd = self.make(*args)
        logger.info('sending request: ' + repr(cmd))
        try:
            send_cmd(self.sock, cmd)
            cmd = recv_cmd(self.sock)
        except socket.error as e:
            logger(repr(e))
            self.app.ErrorExit(u'服务器连接失败！')
        else:
            return cmd[1]

class BroadcastReceiver(threading.Thread):

    def __init__(self, app):
        self.app = app
        threading.Thread.__init__(self)
        self.handle = None
        self.make = RequestMaker()
        self.sock = None
        self.running = True

    def set_handler(self, handler):
        self.handle = handler

    def connect(self):
        result = connect_to_server()
        if isinstance(result, unicode):
            return result
        else:
            self.sock = result
            self.sock.settimeout(None)
            self.running = True
            return None
    
    def run(self):
        try:
            while self.running:
                cmd = self.make(WATCHDOG)
                send_cmd(self.sock, cmd)
                cmd = recv_cmd(self.sock)
                self.handle_broadcast(cmd)
        except socket.error as e:
            logger.error(repr(e))
        finally:
            self.app.Exit()
            
    def handle_broadcast(self, cmd):
        logger.info('handling broadcast: ' + repr(cmd))
        self.handle(cmd)
        if cmd[0] == LOGOUT and cmd[1][0] == self.app.user_name:
            logger.info('receiver stop running...')
            self.running = False
            self.app.Exit()

    def stop_running(self):
        if self.sock:
            logger.info('shuting down socket...')
            self.sock.shutdown(socket.SHUT_RDWR)

        
class RequestMaker():
    def __init__(self):
        self.makers = [
            self.make_signin,
            self.make_login,
            self.make_logout,
            self.make_user_info,
            self.make_talk,
            self.make_kickout,
            self.make_shutup,
            self.make_unshutup,
            self.make_user_detail,
            self.make_watchdog,
        ]
        
    def make(self, type, *args):
        return self.makers[type](*args)

    __call__ = make

    def make_signin(self, user_name, password):
        return SIGNIN, (user_name, password)

    def make_login(self, user_name, password):
        return LOGIN, (user_name, password)

    def make_logout(self, user_name):
        return LOGOUT, (user_name,)
        
    def make_user_info(self, user_name):
        return USER_INFO, (user_name,)

    def make_talk(self, user_name, msg):
        return TALK, (user_name, msg)

    def make_kickout(self, user_name, name):
        return KICKOUT, (user_name, name)

    def make_shutup(self, user_name, name, minutes):
        return SHUTUP, (user_name, name, minutes)

    def make_unshutup(self, user_name, name):
        return UNSHUTUP, (user_name, name)

    def make_user_detail(self, name):
        return USER_DETAIL, (name,)

    def make_watchdog(self):
        return WATCHDOG,
