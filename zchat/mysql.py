# -*- coding:utf-8 -*-
import MySQLdb
from zchat import Logger

logger = Logger('mysql')
class MySQLHandler:
    def __init__(self, host='localhost',
                 user='root', passwd='passw0rd',
                 db='zchat', charset='utf8'):
        # connect to the database
        try:
            self.conn = MySQLdb.connect(host=host, user=user,
                                        passwd=passwd, db=db,
                                        charset=charset);
        except Exception as e:
            logger.error('Failed to connect to the database...')
            logger.error('Message : ' + str(e))
            raise e
        self.cursor = self.conn.cursor()
        logger.info('Connected to the database!')
        
    def closeDB(self):
        self.cursor.close()
        self.conn.close()
        logger.info('Database disconnected!')
        
    def signin(self, user_name, password, user_type=1):
        sql = \
        """
        SELECT * FROM tb_user
        WHERE user_name = %s
        """
        param = user_name,
        if self.cursor.execute(sql, param):
            return False
        sql = \
        """
        INSERT INTO tb_user(user_name, password, user_type)
        VALUES(%s, %s, %s)
        """
        param = user_name, password, user_type
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('signin %r for type %d'
                         % (user_name, user_type))
        return True

    def _confirm(self, user_name, password):
        sql = \
        """
        SELECT user_type FROM tb_user
        WHERE user_name = %s
        """
        param = [user_name]
        if not self.cursor.execute(sql, param):
            return -2 # wrong user name
        sql += " AND password = %s"
        param.append(password)
        if not self.cursor.execute(sql, param):
            return -1 # wrong passwrod
        for row in self.cursor.fetchall():
            return row[0] # return the type of the user

    def login(self, user_name, password):
        user_type = self._confirm(user_name, password)
        if user_type < 0:
            return user_type
        sql = \
        """
        UPDATE tb_user
        SET last_login_time = now(),
            online = 1
        WHERE user_name = %s
        """
        param = user_name,
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('login %r' % user_name)
        return user_type

    def logout(self, user_name):
        sql = \
        """
        UPDATE tb_user
        SET total_online_time = total_online_time +
        TIMESTAMPDIFF(SECOND, last_login_time, now()),
            online = 0
        WHERE user_name = %s
        """
        param = user_name,
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('logout %r' % user_name)

    def kickout(self, user_name):
        sql = \
        """
        UPDATE tb_user
        SET total_online_time = total_online_time +
        TIMESTAMPDIFF(SECOND, last_login_time, now()),
            online = 0
        WHERE user_name = %s
        """
        param = user_name,
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('kickout %r' % user_name)
        
    def shutup(self, user_name, minutes):
        sql = \
        """
        UPDATE tb_user
        SET shutup_until = DATE_ADD(now(), INTERVAL %s MINUTE),
            shutup = 1
        WHERE user_name = %s
        """
        param = minutes, user_name
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('shutup %r for %d minutes'
                         % (user_name, minutes))

    def unshutup(self, user_name):
        sql = \
        """
        UPDATE tb_user
        SET shutup = 0
        WHERE user_name = %s
        """
        param = user_name,
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('unshutup %r' % user_name)

    def record_msg(self, user_name, msg):
        sql = \
        """
        INSERT INTO tb_msg(user_name, recv_time, msg)
        VALUES(%s, now(), %s)
        """
        param = user_name, msg
        self.cursor.execute(sql, param)
        self.conn.commit()
        logger.info('record msg: %r:%r '
                    % (user_name, msg))

    def get_user_info(self, user_name):
        INFO_COLUMNS = [
            'user_name',
            'user_type',
            'shutup'
        ]
        sql = \
        """
        SELECT %s FROM tb_user
        WHERE user_name != %s
        AND online = 1
        """ % (','.join(INFO_COLUMNS), '%s')
        param = user_name,
        self.cursor.execute(sql, param)
        result = []
        for row in self.cursor.fetchall():
            result.append(row)
        return result

    def get_user_detail(self, user_name):
        DETAIL_COLUMNS = [
            'user_name',
            'user_type',
            'online',
            'shutup',
            'TIMESTAMPDIFF(SECOND, now(), shutup_until)',
            'last_login_time',
            'total_online_time + TIMESTAMPDIFF(SECOND, last_login_time, now())',
        ]
        sql = \
        """
        SELECT %s FROM tb_user
        WHERE user_name = %s
        """ % (','.join(DETAIL_COLUMNS), '%s')
        param = user_name,
        self.cursor.execute(sql, param)
        for row in self.cursor.fetchall():
            return row
