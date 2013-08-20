# -*- coding:utf-8 -*-
from twisted.internet import protocol, reactor
from twisted.protocols import basic
from zchat import *
import mysql
logger = Logger('server')

class RequestHandler():

    def __init__(self, mysql_handler):
        self.mysql_handler = mysql_handler
        self.handlers = [
            self.handle_signin,
            self.handle_login,
            self.handle_logout,
            self.handle_user_info,
            self.handle_talk,
            self.handle_kickout,
            self.handle_shutup,
            self.handle_unshutup,
            self.handle_user_detail
        ]

    def handle_cmd(self, cmd):
        return self.handlers[cmd[0]](cmd[1])

    __call__ = handle_cmd

    def handle_signin(self, cmd):
        if not self.mysql_handler:
            return None
        if not self.mysql_handler.signin(*cmd):
            msg = False, u'用户名已存在！'
        else:
            msg = True,
        return (SIGNIN, msg), None

    def handle_login(self, cmd):
        if not self.mysql_handler:
            return None
        user_type = self.mysql_handler.login(*cmd)
        if user_type==TYPE_NOT_EXISTS:
            msg = False, u'用户不存在！'
        elif user_type==TYPR_WRONG_PASSWORD:
            msg = False, u'密码错误！'
        else:
            msg = True,
        reply = LOGIN, msg
        if user_type >= 0:
            msg = user_type, cmd[0]
            broadcast = LOGIN, msg
        else:
            broadcast = None
        return reply, broadcast
                    
    def handle_logout(self, cmd):
        self.mysql_handler.logout(*cmd)
        return (LOGOUT, True), (LOGOUT, cmd)
       
    def handle_user_info(self, cmd):
        msg = self.mysql_handler.get_user_info(*cmd)
        return (USER_INFO, msg), None

    def handle_talk(self, cmd):
        self.mysql_handler.record_msg(*cmd)
        return (TALK, True), (TALK, cmd)
        
    def handle_kickout(self, cmd):
        self.mysql_handler.kickout(*cmd[1:])
        return (KICKOUT, True), (KICKOUT, cmd)

    def handle_shutup(self, cmd):
        self.mysql_handler.shutout(*cmd[1:])
        return (SHUTUP, True), (SHUTUP, cmd)

    def handle_unshutup(self, cmd):
        self.mysql_handler.unshutup(*cmd[1:])
        return (UNSHUTUP, True), (UNSHUTUP, cmd)

    def handle_user_detail(self, cmd):
        msg = self.mysql_handler.get_user_detail(*cmd)
        return (USER_DETAIL, msg), None

class ZChatServerProtocol(basic.LineReceiver):
    
    def connectionMade(self):
        logger.info('connection made with : ' +
                    str(self.transport.getPeer()))

    def lineReceived(self, line):
        logger.info('received : %r' % line)
        cmd = LINE_TO_CMD(line)
        if cmd[0] == WATCHDOG:
            logger.info('received watch dog signal from: ' +
                        str(self.transport.getPeer()))
            self.factory.receivers.add(self.transport)
        else:
            logger.info('handling request: ' + repr(cmd))
            reply, broadcast = self.factory.handle_request(cmd)
            self.sendReply(reply)
            self.sendBroadcast(broadcast)
        
    def sendReply(self, cmd):
        if not cmd: return
        logger.info('sending reply: ' + repr(cmd))
        line = CMD_TO_LINE(cmd)
        self.transport.write(line)
        if cmd[0] == LOGOUT:
            logger.info('losting connection with : ' +
                        str(self.transport.getPeer()))
            self.transport.loseConnection()

    def sendBroadcast(self, cmd):
        if not cmd: return
        logger.info('sending broadcast: ' + repr(cmd))
        line = CMD_TO_LINE(cmd)
        for receiver in self.factory.receivers:
            try:
                receiver.write(line)
            except socket.error as e:
                logger(repr(e))
                logger('removing receiver : ' + receiver.getPeer())
                self.factory.receivers.remove(receiver)

class ZChatServerFactory(protocol.ServerFactory):
    
    protocol = ZChatServerProtocol

    def __init__(self):
        self.receivers = set()
        self.mysql_handler = mysql.MySQLHandler()
        self.handle_request = RequestHandler(self.mysql_handler)

factory = ZChatServerFactory()
reactor.listenTCP(PORT, factory)
# reactor.callLater(5, reactor.stop)
reactor.run()
factory.mysql_handler.closeDB()
