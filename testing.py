from general import Connection
import os

if __name__ == '__main__':
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    ip = '192.168.3.10'
    devicetype = 'cisco_ios_telnet'
    session = Connection(ip, username, password, devicetype, True, 'testing123').connection().session
    print(session.send_command('show run', use_textfsm=True))
