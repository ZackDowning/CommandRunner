from gui import ManagementFileBrowseWindow
from general import Connection, mt, Connectivity
from getpass import getpass


def command_runner():
    mgmt_ips = ManagementFileBrowseWindow().mgmt_ips


if __name__ == '__main__':
    mgmt_ips = ManagementFileBrowseWindow().mgmt_ips
