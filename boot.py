# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import machine
import network

lan = network.LAN(mdc = machine.Pin(16), mdio = machine.Pin(17), power = None,
phy_type = network.PHY_RTL8201, phy_addr = 0)
lan.active(1)
