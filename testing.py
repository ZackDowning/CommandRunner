from general import Connection
import os
# import re

if __name__ == '__main__':
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    ip = '192.168.3.10'
    devicetype = 'cisco_ios_telnet'
    with Connection(ip, username, password, devicetype, True, 'testing123').connection().session as session:
        print(session.send_command('show run', use_textfsm=True))
    print('Done')
