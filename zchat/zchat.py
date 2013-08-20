# -*- coding:utf-8 -*-
import logging, time, pickle, md5

CURRENT_TIME = lambda: time.strftime("%Y-%m-%d %H:%M:%S")
CMD_TO_LINE = lambda cmd: pickle.dumps(cmd) + '\r\n'
LINE_TO_CMD = lambda line: pickle.loads(line)
MD5_CONVERT = lambda s: md5.md5(s).hexdigest().decode('utf-8')

# PORT AND HOST
PORT = 2442
HOST = 'localhost'
TIMEOUT = 10

# define commonds
SIGNIN,                                \
LOGIN,                                 \
LOGOUT,                                \
USER_INFO,                             \
TALK,                                  \
KICKOUT,                               \
SHUTUP,                                \
UNSHUTUP,                              \
USER_DETAIL,                           \
WATCHDOG,                              \
= range(10)

# define user types
TYPE_NOT_EXISTS,                       \
TYPR_WRONG_PASSWORD,                   \
TYPE_ADMIN,                            \
TYPE_NORMAL,                           \
= range(-2, 2)

class Logger():
    
    LOG_FILENAME = 'zchat.log'
    
    def __init__(self, header):
        logging.basicConfig(#filename = sys.LOG_FILENAME,
                            level = logging.DEBUG)
        self.header = header
    def info(self, msg):
        logging.info(CURRENT_TIME() + '==>' + self.header + ':' + msg)

    __call__ = info
        
    def error(self, msg):
        logging.error(CURRENT_TIME() + '==>' + self.header + ':' + msg)
