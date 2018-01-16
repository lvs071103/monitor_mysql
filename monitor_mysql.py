#!/usr/bin/env python
# coding=utf8
# author: Jack.Z


import sys
import optparse
import MySQLdb
import MySQLdb.cursors


class Monitor(object):

    def __init__(self, **params):
        self.__session = None
        self.__connection = None
        self.__open = None
        self.__getStatus = None
        self.result = None
        self.dict = {}
        self.user = params['user']
        self.password = params['password']
        self.host = params['host']
        self.port = int(params['port'])

    def open(self):
        """
        open mysql connection
        """
        try:
            cnx = MySQLdb.connect(host=self.host,
                                  user=self.user,
                                  passwd=self.password,
                                  port=self.port,
                                  cursorclass=MySQLdb.cursors.DictCursor
                                  )
            self.__connection = cnx
            self.__session = cnx.cursor()
        except MySQLdb.Error as e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def close(self):
        self.__session.close()
        self.__connection.close()

    def getStatus(self):
        try:
            cursor = self.__connection.cursor()
            cursor.execute("SHOW GLOBAL STATUS")
            self.result = cursor.fetchall()
            for item in self.result:
                self.dict[item['Variable_name']] = item['Value']
            return self.dict
        except Exception, e:
            print e

    def get_some_status(self, key):
        return self.dict[key]

    def tps(self):
        return int(self.dict['Com_commit']) + int(self.dict['Com_rollback'])

    def qps(self):
        return int(self.dict['Com_insert']) + int(self.dict['Com_delete']) + \
               int(self.dict['Com_select']) + int(self.dict['Com_update'])

    def key_read_hit_ratio(self):
        try:
            return (1 - float(self.dict['Key_reads']) / float(self.dict['Key_read_requests'])) * 100
        except ZeroDivisionError, e:
            print "integer division or modulo by zero", e

    def key_usage_ratio(self):
        try:
            return float(self.dict['Key_blocks_used']) / (float(self.dict['Key_blocks_used']) +
                                                          float(self.dict['Key_blocks_unused']))
        except ZeroDivisionError, e:
            print "integer division or modulo by zero", e

    def key_write_hit_ratio(self):
        try:
            return (1 - float(self.dict['Key_writes']) / float(self.dict['Key_write_requests'])) * 100
        except ZeroDivisionError, e:
            print "integer division or modulo by zero", e

    def innodb_buffer_read_hit_ratio(self):
        try:
            return (1 - float(self.dict['Innodb_buffer_pool_reads']) /
                    float(self.dict['Innodb_buffer_pool_read_requests'])) * 100
        except ZeroDivisionError, e:
            print "integer division or modulo by zero", e

    def innodb_buffer_usage(self):
        try:
            return (1 - float(self.dict['Innodb_buffer_pool_pages_free']) /
                    float(self.dict['Innodb_buffer_pool_pages_total'])) * 100
        except ZeroDivisionError, e:
            print "integer division or modulo by zero", e

    def innodb_buffer_pool_dirty_ratio(self):
        try:
            return (float(self.dict['Innodb_buffer_pool_pages_dirty']) /
                    float(self.dict['Innodb_buffer_pool_pages_total'])) * 100
        except ZeroDivisionError, e:
            print "integer division or modulo by zero", e


class Main(object):

    def __init__(self):
        self.opt = None
        self.debug = None
        self.actions = None
        self.options = None
        self.params = dict()

    @staticmethod
    def trans_string(name):
        lower = False
        new_name = ""
        for i in name:
            if i == '_':
                lower = True
                continue
            if lower:
                new_name += i.lower()
            else:
                new_name += i
            lower = False
        return new_name

    def run(self):
        actions = []
        usage = "%prog Actions [options] \nUse this script monitor mysql status."

        self.opt = optparse.OptionParser(version='v1.0', usage=usage)
        self.opt.add_option('--debug', dest='debug', action='store_true', default=False, help='Print debug information')
        self.opt.add_option('-H', '--host', dest='host', help='mysql hostname or ip address')
        self.opt.add_option('-u', '--user', dest='user', help='connect mysql username')
        self.opt.add_option('-p', '--password', dest='password', help='connect mysql password')
        self.opt.add_option('-P', '--port', dest='port', help='mysql port')
        self.opt.add_option('-k', '--key', dest='key', default=None, help='get some key status')

        if len(sys.argv) < 2:
            self.opt.print_help()
            return 0

        if len(sys.argv) == 2:
            self.opt.print_help()
            return 0

        (options, args) = self.opt.parse_args()

        self.debug = options.debug
        if not args[0] == 'get_some_status':
            del options.key

        for key in dir(options):
            if not key.startswith("_") and getattr(options, key) is None:
                raise KeyError, ('Error: Please provide options --%s' % key)

        for option in self.opt.option_list:
            if option.dest not in [None, 'debug', 'fun', 'key']:
                self.params[self.trans_string(option.dest)] = getattr(options, option.dest)

        my_instance = Monitor(**self.params)
        for item in dir(my_instance):
            if not item.startswith("_") and item not in [
                'close', 'open', 'getStatus', 'host', 'open', 'password', 'result', 'user', 'dict'
            ]:
                actions.append(item)

        action = sys.argv[1]
        if action not in actions:
            self.opt.print_help()
            print "Right actions include: \n{Actions}".format(Actions=actions)
            return 0

        self.options = options
        self.actions = actions

        my_instance.open()
        status = my_instance.getStatus()
        if hasattr(my_instance, args[0]):
            if args[0] == 'get_some_status':
                if options.key not in status.keys():
                    print('Error: Please provide right key; mysql command: SHOW GLOBAL STATUS')
                else:
                    print my_instance.get_some_status(key=options.key)
            else:
                print getattr(my_instance, args[0])()
        my_instance.close()


if __name__ == "__main__":
    Main().run()
