import os
import sys
from concurrent.futures import ThreadPoolExecutor, wait
from netmiko import ConnectHandler, ssh_exception, SSHDetect
from icmplib import ping
from exceptions import TemplatesNotFoundWithinPackage
from address_validator import ipv4

# Checks for TextFSM templates within single file bundle if code is frozen
if getattr(sys, 'frozen', False):
    os.environ['NET_TEXTFSM'] = sys._MEIPASS
else:
    for path in sys.path:
        if path.__contains__('site-packages'):
            if os.path.exists(f'{path}/CiscoIPScanner/templates'):
                os.environ['NET_TEXTFSM'] = f'{path}/CiscoIPScanner/templates'
            elif os.path.exists('./CiscoIPScanner/templates'):
                os.environ['NET_TEXTFSM'] = './CiscoIPScanner/templates'
            else:
                raise TemplatesNotFoundWithinPackage


class MgmtIPAddresses:
    """Input .txt file location containing list of management IP addresses"""
    def __init__(self, mgmt_file_location):
        self.mgmt_file_location = mgmt_file_location
        self.mgmt_ips = []
        """Formatted set of validated IP addresses"""
        self.invalid_line_nums = []
        """Set of invalid line numbers corresponding to line number of management file input"""
        self.invalid_ip_addresses = []
        """Set of invalid IP addresses"""
        self.validate = True
        """Bool of management IP address file input validation"""
        with open(self.mgmt_file_location) as file:
            for idx, address in enumerate(file):
                ip_address = str(address).strip('\n')
                if ipv4(ip_address) is False:
                    self.invalid_line_nums.append(str(idx + 1))
                    self.invalid_ip_addresses.append(str(address))
                    self.validate = False
                    """Bool of management IP address file input validation"""
                else:
                    self.mgmt_ips.append(ip_address)


def reachability(ip_address, count=4):
    """Returns bool if host is reachable with default count of 4 pings"""
    return ping(ip_address, privileged=False, count=count).is_alive


class Connection:
    """SSH or TELNET Connection Initiator"""
    def __init__(self, ip_address, username, password, devicetype='autodetect', con_type=None):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.hostname = ''
        self.devicetype = devicetype
        self.con_type = con_type
        self.exception = 'None'
        self.authentication = False
        self.authorization = False
        self.connectivity = False
        self.session = None
        self.device = {
            'device_type': self.devicetype,
            'ip': ip_address,
            'username': username,
            'password': password
        }

    def check(self):
        """Base connectivity check method of device returning updated self attributes:\n
        devicetype\n
        hostname\n
        con_type\n
        exception\n
        authentication\n
        authorization\n
        connectivity"""
        if reachability(self.ip_address):
            try:
                try:
                    autodetect = SSHDetect(**self.device).autodetect()
                    self.device['device_type'] = autodetect
                    self.devicetype = autodetect
                    self.session = ConnectHandler(**self.device)
                except ValueError:
                    try:
                        self.device['device_type'] = 'cisco_ios'
                        self.devicetype = 'cisco_ios'
                        self.session = ConnectHandler(**self.device)
                    except ValueError:
                        self.device['device_type'] = 'cisco_ios'
                        self.devicetype = 'cisco_ios'
                        self.session = ConnectHandler(**self.device)
                showver = self.session.send_command('show version', use_textfsm=True)
                if not showver.__contains__('Failed'):
                    self.hostname = showver[0]['hostname']
                    self.authorization = True
                self.authentication = True
                self.connectivity = True
                self.con_type = 'SSH'
            except (ConnectionRefusedError, ValueError, ssh_exception.NetmikoAuthenticationException,
                    ssh_exception.NetmikoTimeoutException):
                try:
                    try:
                        self.device['device_type'] = 'cisco_ios_telnet'
                        self.devicetype = 'cisco_ios_telnet'
                        self.device['secret'] = self.password
                        self.session = ConnectHandler(**self.device)
                        showver = self.session.send_command('show version', use_textfsm=True)
                        if not showver.__contains__('Failed'):
                            self.hostname = showver[0]['hostname']
                            self.authorization = True
                        self.authentication = True
                        self.connectivity = True
                        self.con_type = 'TELNET'
                    except ssh_exception.NetmikoAuthenticationException:
                        self.device['device_type'] = 'cisco_ios_telnet'
                        self.devicetype = 'cisco_ios_telnet'
                        self.device['secret'] = self.password
                        self.session = ConnectHandler(**self.device)
                        showver = self.session.send_command('show version', use_textfsm=True)
                        if not showver.__contains__('Failed'):
                            self.hostname = showver[0]['hostname']
                            self.authorization = True
                        self.authentication = True
                        self.connectivity = True
                        self.con_type = 'TELNET'
                except ssh_exception.NetmikoAuthenticationException:
                    self.connectivity = True
                    self.exception = 'NetmikoAuthenticationException'
                except ssh_exception.NetmikoTimeoutException:
                    self.exception = 'NetmikoTimeoutException'
                except ConnectionRefusedError:
                    self.exception = 'ConnectionRefusedError'
                except ValueError:
                    self.exception = 'ValueError'
                except TimeoutError:
                    self.exception = 'TimeoutError'
            except OSError:
                self.exception = 'OSError'
            if self.session is not None:
                self.session.disconnect()
        else:
            self.exception = 'NoPingEcho'
        return self

    def connection(self):
        """Base connection method\n
        Should only use self attributes:\n
        session\n
        exception"""
        if reachability(self.ip_address):
            try:
                if self.con_type == 'TELNET':
                    self.device['secret'] = self.password
                    self.session = ConnectHandler(**self.device)
                else:
                    self.session = ConnectHandler(**self.device)
            except ConnectionRefusedError:
                self.exception = 'ConnectionRefusedError'
            except ssh_exception.NetmikoAuthenticationException:
                self.exception = 'NetmikoAuthenticationException'
            except ssh_exception.NetmikoTimeoutException:
                self.exception = 'NetmikoTimeoutException'
            except ValueError:
                self.exception = 'ValueError'
            except TimeoutError:
                self.exception = 'TimeoutError'
            except OSError:
                self.exception = 'OSError'
        else:
            self.exception = 'NoPingEcho'
        return self


def mt(function, iterable, threads=50):
    executor = ThreadPoolExecutor(threads)
    futures = [executor.submit(function, val) for val in iterable]
    wait(futures, timeout=None)
