# This file is executed on every boot (including wake-boot from deepsleep)

## Going to use https://github.com/RangerDigital/senko/ to allow for OTA updates.
## Walking down to the basement with a laptop and UART cable to make minor updates sounds like a draaaag
import gc
import machine
import network
import ntptime
from time import sleep, localtime


# Specific to the wESP32 >Rev7
def connect_wired_ethernet():
    lan = network.LAN(mdc = machine.Pin(16), mdio = machine.Pin(17), power = None,
    phy_type = network.PHY_RTL8201, phy_addr = 0)
    lan.active(1)
    print('Waiting on IP',end='')
    for x in range(30):
        print('.',end='')
        if lan.isconnected():
            if lan.ifconfig()[0] is not '0.0.0.0':
                print('')
                print(lan.ifconfig())
                break
        sleep(1)

def set_yer_clock():
    ntptime.host = '192.168.1.1'
    print(f'Setting clock via NTP from {ntptime.host}', end='')
    for x in range(3):
        print('.',end='')
        try:
            ntptime.settime()
        except:
            sleep(10)
    print('')
    print(localtime())

def main():
    gc.collect()
    gc.enable()
    connect_wired_ethernet()
    set_yer_clock()
    print('Exiting boot.py; hello main.py!')

if __name__ == "__main__":
    main()

