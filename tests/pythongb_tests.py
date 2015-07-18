from nose.tools import *
from pythongb.cpu import *

# The testing of the correctness of opcodes will be done using a test rom

def test_cpu():
    gbcpu = CPU()

    # Go through each opcode and execute every one
    # This will find syntactical errors
    ignore = [0xcb, 0x3b, 0xd3, 0xdb, 0xdd, 0xde, 0xe3, 0xe4, 0xeb, 0xec, 0xed, 0xf4, 0xfc, 0xfd]

    for i in range(256):
        if i in ignore:
            continue

        gbcpu.executeOpcode(i)


    # Now test all the 0xCB opcodes
    tests = [0x37,
            0x30,
            0x31,
            0x32,
            0x33,
            0x34,
            0x35,
            0x36,
            0x07,
            0x00,
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x17,
            0x10,
            0x11,
            0x12,
            0x13,
            0x14,
            0x15,
            0x16,
            0x0F,
            0x08,
            0x09,
            0x0A,
            0x0B,
            0x0C,
            0x0D,
            0x0E,
            0x1F,
            0x18,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
            0x27,
            0x20,
            0x21,
            0x22,
            0x23,
            0x24,
            0x25,
            0x26,
            0x2F,
            0x28,
            0x29,
            0x2A,
            0x2B,
            0x2C,
            0x2D,
            0x2E,
            0x3F,
            0x38,
            0x39,
            0x3A,
            0x3B,
            0x3C,
            0x3D,
            0x3E]

    for n in tests:
        gbcpu.cbtable_test(n)


