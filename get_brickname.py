import random
import time
import struct
import usb.core
import usb.util
import sys
from cStringIO import StringIO

ID_VENDOR_LEGO = 0x0694
ID_PRODUCT_EV3 = 0x0005

DIRECT_COMMAND_REPLY = 0x00
EP_IN = 0x81
EP_OUT = 0x01


def write_message(dev, message):
    message = struct.pack('<H', len(message)) + message
    dev.write(EP_OUT, message, 0, 100)


def get_brickname(dev):
    counterout = random.randint(1, 200)
    sout = StringIO()
    sout.write(struct.pack('<H', counterout))
    sout.write(struct.pack('B', DIRECT_COMMAND_REPLY))
    sout.write(struct.pack('B', 0x06))  # 00001100 two variables: see lms2012/lms2012/doc/html/directcommands.html
    sout.write(struct.pack('B', 0x00))  # 00000000
    sout.write(struct.pack('B', 0xD3))  # opCOM_GET
    sout.write(struct.pack('B', 13))    # GET_BRICKNAME
    sout.write(struct.pack('B', 0x06))  # LC0(6) Local Constant
    sout.write(struct.pack('B', 0x60))  # GV0(0) Global Variable for response
    message = sout.getvalue()
    write_message(dev, message)
    ret = dev.read(EP_IN, 1024, 0, 100)

    sin = StringIO(ret)
    cmd_size = struct.unpack('<H', sin.read(2))
    counterin = struct.unpack('<H', sin.read(2))
    cmd_type = struct.unpack('B', sin.read(1))
    brickname = []

    value = sin.read(1)
    while value != '\x00':
        brickname.append(value)
        value = sin.read(1)

    return ''.join(brickname)


def main():

    dev = usb.core.find(idVendor=ID_VENDOR_LEGO, idProduct=ID_PRODUCT_EV3)

    if dev is None:
        print "No Lego EV3 found"

    else:
        interface = 0
        print "Lego EV3 brick found"
        if dev.is_kernel_driver_active(interface) is True:
            print "Linux Kernel driver attached, need to detach it first"
            dev.detach_kernel_driver(interface)

        print "claiming device"
        dev.set_configuration()
        usb.util.claim_interface(dev, interface)

        # XXX Hack. Clean up the USB buffer, but why?
        dev.read(0x81, 1024, 0, 100)

        brickname = get_brickname(dev)
        print "Lego EV3 brickname is:", brickname

        print "all done"
        return 0

if __name__ == '__main__':
    main()
