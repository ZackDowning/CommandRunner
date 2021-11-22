from gui import ManagementFileBrowseWindow, ConfigFileBrowseWindow
from net_async import AsyncSessions, ForceSessionRetry
from getpass import getpass
import re
import time

# TODO: Add support for config file

# PyInstaller bundle command:
# pyinstaller -F --hidden-import PySimpleGUI,net_async --add-data templates;templates main.py

banner = '   ______                                          ______                             \n' \
         '  / ____/___  ____ ___  ____ ___  ____ _____  ____/ / __ \\__  ______  ____  ___  _____\n' \
         ' / /   / __ \\/ __ `__ \\/ __ `__ \\/ __ `/ __ \\/ __  / /_/ / / / / __ \\/ __ \\/ _ \\/ ___/\n' \
         '/ /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ / _, _/ /_/ / / / / / / /  __/ /    \n' \
         '\\____/\\____/_/ /_/ /_/_/ /_/ /_/\\__,_/_/ /_/\\__,_/_/ |_|\\__,_/_/ /_/_/ /_/\\___/_/     \n'


# Outputs failed device list to CSV file with columns:
# 'ip_address,connectivity,authentication,authorization,con_type,con_exception'
def output_failed_to_file(failed_list):
    with open('failed_devices.csv', 'w+') as file:
        file.write(
            'ip_address,connectivity,authentication,authorization,con_exception\n'
        )
        for device in failed_list:
            ip_address = device['ip_address']
            connectivity = device['connectivity']
            authentication = device['authentication']
            authorization = device['authorization']
            exception = device['exception']
            file.write(
                f'{ip_address},{connectivity},{authentication},{authorization},{exception}\n'
            )


def command_runner():
    def cr(session):
        save_cmd = ''
        if session.devicetype == 'cisco_ios' or session.devicetype == 'cisco_ios_telnet':
            save_cmd = 'wr'
        elif session.devicetype == 'cisco_nxos':
            save_cmd = 'copy run start'
        try:
            if commands[0] != '':
                cmd = session.send_config_set(commands)
                if cmd.__contains__('Authorization failed'):
                    raise ForceSessionRetry
        except IndexError:
            pass
        if save:
            session.session.fast_cli = False
            cmd = session.send_command(save_cmd)
            # cmd = session.session.save_config()
            if cmd.__contains__('Authorization failed'):
                raise ForceSessionRetry

    mgmt_ips = ManagementFileBrowseWindow().mgmt_ips
    print(banner)
    try:
        if len(mgmt_ips) == 0:
            print('No IP addresses found in file provided.')
            input('Press Enter to close.')
    except TypeError:
        print('No file provided.')
        input('Press Enter to close.')
    else:
        username = input('Enter Username: ')
        password = getpass('Enter Password: ')
        enable_pw = getpass('(If applicable) Enter Enable Password: ')
        while True:
            commands = input(
                """Type 'use_file' if you want to provide configuration file, or
enter configuration commands separating each command with a comma and no space.
Example: interface vlan 1,no ip address,shut
Commands: """
            ).split(',')
            if 'use_file' in commands[0]:
                commands = ConfigFileBrowseWindow().cmds
            while True:
                save = input('Do you want to save the config? [Y]/N: ')
                if re.fullmatch(r'[Yy]|', save):
                    save = True
                    break
                elif re.fullmatch(r'[Nn]', save):
                    save = False
                    break
            start = time.perf_counter()
            print('Sending commands to devices...\n'
                  '------------------------------------------------')
            sessions = AsyncSessions(username, password, mgmt_ips, cr, enable_pw, True)
            end = time.perf_counter()
            print(f'------------------------------------------------'
                  f'\nCommands ran in {int(round(end - start, 0))} seconds.')
            if len(sessions.failed_devices) != 0:
                print('See failed_devices.csv for more information on failed devices')
                output_failed_to_file(sessions.failed_devices)
            print('\nFinished.')
            more_cmds = input('Do you want to send more commands? Y/[N]: ')
            if re.fullmatch(r'[Yy]', more_cmds):
                continue
            elif re.fullmatch(r'[Nn]|', more_cmds):
                break
            else:
                break
        input('Press Enter to close.')


if __name__ == '__main__':
    command_runner()
