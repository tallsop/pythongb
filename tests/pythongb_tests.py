from nose.tools import *
from pythongb.cpu import *

# The testing of the correctness of opcodes will be done using a test rom

def test_cpu():
    gbcpu = CPU()

    # Go through each opcode and execute every one
    # This will find syntactical errors
    for i in range(256):
        gbcpu.executeOpcode(i)
