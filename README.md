# CommandRunner
One-file executable for running sets of configuration commands on Cisco IOS(-XE) and NX-OS devices asynchronously.

General use case is for simple and fast configuration management at scale.
## Requirements
- Windows Operating System to run executable on
- Text file with list of management IP addresses for devices
  - Example: example.txt
    ```
    1.1.1.1
    2.2.2.2
    3.3.3.3
    ```
- Administration credentials for devices
- ICMP ping reachability to management IP addresses of devices
- Device running Cisco IOS, IOS-XE, or NX-OS operating system
- Optional configuration file
  - Example: example.txt
    ```
    interface vlan 1
    no ip address
    shut
    ```
## Executable Windows
### Management IP Address File Selection
![](https://i.imgur.com/DM1l7NL.png)
### Config File Selection
![](https://gcdn.pbrd.co/images/koyijkr3weP5.png?o=1)
### Terminal
![](https://gcdn.pbrd.co/images/puBX6YRHfEAn.png?o=1)