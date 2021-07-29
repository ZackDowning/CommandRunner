from gui import ManagementFileBrowseWindow
from general import Connection, MultiThread, Connectivity
from getpass import getpass
import re
import time

# TODO: Add comments

banner = '   ______                                          ______                             \n'\
         '  / ____/___  ____ ___  ____ ___  ____ _____  ____/ / __ \\__  ______  ____  ___  _____\n'\
         ' / /   / __ \\/ __ `__ \\/ __ `__ \\/ __ `/ __ \\/ __  / /_/ / / / / __ \\/ __ \\/ _ \\/ ___/\n'\
         '/ /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ / _, _/ /_/ / / / / / / /  __/ /    \n'\
         '\\____/\\____/_/ /_/ /_/_/ /_/ /_/\\__,_/_/ /_/\\__,_/_/ |_|\\__,_/_/ /_/_/ /_/\\___/_/     \n'


# Outputs failed device list to CSV file with columns:
# 'ip_address,connectivity,authentication,authorization,con_type,con_exception'
def output_failed_to_file(failed_list):
    with open('failed_devices.csv', 'w+') as file:
        file.write(
            'ip_address,connectivity,authentication,authorization,con_exception\n'
        )
        for device in failed_list:
            ip_address = device['ip']
            connectivity = device['connectivity']
            authentication = device['authentication']
            authorization = device['authorization']
            exception = device['exception']
            file.write(
                f'{ip_address},{connectivity},{authentication},{authorization},{exception}\n'
            )


class CommandRunner:
    def __init__(self):
        def command_runner(device):
            save_cmd = ''
            ip_address = device['ip']
            device_type = device['device_type']
            enable = device['enable']
            if device_type == 'cisco_ios' or device_type == 'cisco_ios_telnet':
                save_cmd = 'wr'
            elif device_type == 'cisco_nxos':
                save_cmd = 'copy run start'
            session = Connection(
                ip_address, self.username, self.password, device_type, enable, self.enable_pw).connection().session
            if len(self.commands) != 0:
                session.send_config_set(self.commands)
            if self.save:
                session.send_command(save_cmd)
            print(f'Done: {ip_address}')
            self.finished_devices.append(ip_address)

        self.mgmt_ips = ManagementFileBrowseWindow().mgmt_ips
        print(banner)
        self.username = input('Enter Username: ')
        self.password = getpass('Enter Password: ')
        self.enable_pw = getpass('(If applicable) Enter Enable Password: ')
        while True:
            self.commands = input('(If applicable) Enter config commands seperating each command with a comma and no '
                                  'space.\n'
                                  'Example: interface vlan 1,no ip address,shut\n'
                                  'Commands: ').split(',')
            while True:
                self.save = input('Do you want to save the config? [Y]/N: ')
                if re.fullmatch(r'[Yy]|', self.save):
                    self.save = True
                    break
                elif re.fullmatch(r'[Nn]', self.save):
                    self.save = False
                    break
            print('Testing Connectivity, authentication, and authorization on devices...')
            start = time.perf_counter()
            self.check = Connectivity(self.mgmt_ips, self.username, self.password, self.enable_pw)
            bug_count = 0
            while True:
                self.finished_devices = []
                successful_devices = self.check.successful_devices
                time.sleep(5)
                if bug_count != 0:
                    print('Ran into bug with Windows multithreading. Trying again...')
                print('Sending commands to devices...')
                MultiThread(command_runner, successful_devices).mt()
                if len(self.finished_devices) == len(successful_devices):
                    break
            failed_devices = self.check.failed_devices
            end = time.perf_counter()
            print(f'Connectivity check finished in {int(round(end - start, 0))} seconds.')
            if len(failed_devices) != 0:
                print('See failed_devices.csv for more information on failed devices')
                output_failed_to_file(failed_devices)
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
    CommandRunner()
