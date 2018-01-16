JackdeMacBook-Pro:scripts jack$ python monitor_mysql.py qps --host localhost --user root --password LVS@071103 --port 3306
30836
JackdeMacBook-Pro:scripts jack$ python monitor_mysql.py tps --host localhost --user root --password LVS@071103 --port 3306
92
JackdeMacBook-Pro:scripts jack$ python monitor_mysql.py get_some_status --host localhost --user root --password LVS@071103 --port 3306 --key Innodb_buffer_pool_reads
637
JackdeMacBook-Pro:scripts jack$ python monitor_mysql.py innodb_buffer_read_hit_ratio --host localhost --user root --password LVS@071103 --port 3306
99.9321566723

$ python monitor_mysql.py --help
Usage: monitor_mysql.py Actions [options] 
Use this script monitor mysql status.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --debug               Print debug information
  -H HOST, --host=HOST  mysql hostname or ip address
  -u USER, --user=USER  connect mysql username
  -p PASSWORD, --password=PASSWORD
                        connect mysql password
  -P PORT, --port=PORT  mysql port
  -k KEY, --key=KEY     get some key status

