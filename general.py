import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, wait
from icmplib import ping
from netmiko import ConnectHandler, ssh_exception, SSHDetect
from address_validator import ipv4

# Checks for TextFSM templates within single file bundle if code is frozen
if getattr(sys, 'frozen', False):
    os.environ['NET_TEXTFSM'] = sys._MEIPASS
else:
    os.environ['NET_TEXTFSM'] = './templates'


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
