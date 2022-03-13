# This file is executed on every boot (including wake-boot from deepsleep)

## Going to use https://github.com/RangerDigital/senko/ to allow for OTA updates.
## Walking down to the basement with a laptop and UART cable to make minor updates sounds like a draaaag
import gc
import machine
import network

# Specific to the wESP32 >Rev7
def connect_wired_ethernet():
    lan = network.LAN(mdc = machine.Pin(16), mdio = machine.Pin(17), power = None,
    phy_type = network.PHY_RTL8201, phy_addr = 0)
    lan.active(1)


def main():
    gc.collect()
    gc.enable()

    import senko
    OTA = senko.Senko(user='mjolnerd', repo='SumpMonitor', files=['test.py'])

      if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()

if __name__ == "__main__":
    main()
