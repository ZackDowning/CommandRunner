# from general import Connection
# import os
import re

if __name__ == '__main__':
    # username = os.getenv('USERNAME')
    # password = os.getenv('PASSWORD')
    # ip = '192.168.3.10'
    # devicetype = 'cisco_ios_telnet'
    # session = Connection(ip, username, password, devicetype, True, 'testing123').connection().session
    # print(session.send_command('show run', use_textfsm=True))
    while True:
        print('Finished.')
        more_cmds = input('Do you want to send more commands? [Y]/N: ')
        if re.fullmatch(r'[Yy]|', more_cmds):
            continue
        elif re.fullmatch(r'[Nn]', more_cmds):
            break
        else:
            break
