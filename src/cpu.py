from memory import MemoryController

"""
Registers are defined as dictionaries as they are hashmaps, they allow for O(1) lookup.
F Register - Holds the CPU flags as follows:
7 6 5 4 3 .. 0
Z N H C 0    0 (3 to 0 always 0)

Flag definitions:
Z - Zero flag - 0
N - Subtraction flag - 1
H - Half carry flag - 2
C - Carry flag - 3
"""

class CPU(object):
    def __init__(self):
        # All values are set to their initial values upon the systems startup
        self.r = {
            "a": 0,
            "b": 0,
            "c": 0,
            "d": 0,
            "e": 0,
            "f": 0,
            "h": 0,
            "l": 0,
            "pc": 0x100,
            "sp": 0xFFFE,
            "ime": 1}

        # Initially the flag register is 0?
        self.flag = {
            "z" : 0,
            "n" : 0,
            "h" : 0,
            "c" : 0
        }
        self.memory = MemoryController()

    """ Helper Functions """
    def getHL(self):
        return self.r["h"] << 8 | self.r["l"]

    def getAB(self, a, b):
        return self.r[a] << 8 | self.r[b]

    def incPC(self):
        self.r["pc"] += 1

    def addSP(self, value):
        self.r["sp"] += value

    def addAB(self, a, b, value):
        val = (self.r[a] << 8 | self.r[b]) + value
        self.r[a] = val >> 8
        self.r[b] = 0x00FF & val

    def getFlagAsInt(self):
        return self.flag["z"] << 8 | self.flag["n"] << 7 | self.flag["h"] << 6 | self.flag["c"] << 5

    def set_bit(self, v, index, x):
        """Set the index:th bit of v to x, and return the new value."""
        mask = 1 << index
        v &= ~mask

        if x:
            v |= mask

        return v

    """ Opcode functions are below """

    """ All 8-Bit load functions """
    # Place the value nn into n
    def ldnnn(self, nn):
        # To get n we need to inc pc
        self.incPC()

        n = self.memory.read(self.r["pc"])
        self.r[nn] = n

    # Place the value in reg r2 into r1
    def ldr1r2(self, r1, r2):
        self.r[r1] = self.r[r2]

    # Place value of (HL) into r1
    def ldr1hl(self, r1):
        self.r[r1] = self.memory.read(self.getHL())

    # Write the value in r2 to location (HL)
    def ldhlr2(self, r2):
        self.memory.write(self.getHL(), self.r[r2])

    # Write value n to (HL)
    def ldhln(self):
        self.incPC()

        n = self.memory.read(self.r["pc"])
        self.memory.write(self.getHL(), n)

    # Place the value of register n into A
    def ldan(self, n):
        self.r["a"] = self.r[n]

    # Place the value of (AB) into A
    def ldab(self, a, b):
        self.r["a"] = self.memory.read(self.getAB(a, b))

    # Load a with the value of location nn
    def ldann(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])

        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        self.r["a"] = self.memory.read(n1 << 8 | n2)

    # Load A with an immediate value e (AKA #)
    def ldae(self):
        self.incPC()
        e = self.memory.read(self.r["pc"])

        self.r["a"] = e

    # Put the value in reg A into n
    def ldna(self, n):
        self.r[n] = self.r["a"]

    # Put the value of reg A in (AB)
    def ldaba(self, a, b):
        self.memory.write(self.getAB(a, b), self.r["a"])

    # Put value of reg A into address nn
    def ldann(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])
        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        nn = n1 << 8 | n2

        self.memory.write(nn, self.r["a"])

    # Place value at address 0xFF00 + C into A
    def ldac(self):
        self.r["a"] = self.memory.read(0xFF00 + self.r["c"])

    # Place the value of A into address 0xFF00 + C
    def ldca(self):
        self.memory.write(0xFF00 + self.r["c"], self.r["a"])

    # Put the value at (HL) into A. Decrement HL.
    def lddahl(self):
        self.r = self.memory.read(self.getHL())
        self.addAB("h", "l", -1)

    # Put A into address HL, decrement HL
    def lddhla(self):
        self.memory.write(self.getHL(), self.r["a"])
        self.add("h", "l", -1)

    # Put value at address HL into A. Increment HL
    def ldiahl(self):
        self.r["a"] = self.memory.read(self.getHL())
        self.addAB("h", "l", 1)

    # Put A into memory location A then increment HL
    def ldihla(self):
        self.memory.write(self.getHL(), self.r["a"])
        self.add("h", "l", 1)

    # Put A into address 0xFF00 + n
    def ldhna(self):
        self.incPC()
        address = 0xFF00 + self.memory.read(self.r["pc"])

        self.memory.write(address, self.r["a"])

    # Put memory address 0xFF00 + n in A
    def ldhan(self):
        self.incPC()
        address = 0xFF00 + self.memory.read(self.r["pc"])

        self.memory.write(address, self.r["a"])

    """ All 16 Bit Loads """
    # Place value n1n2 into ab
    def ldnnn16(self, a , b):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])

        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        self.r[a] = n1
        self.r[b] = n2

    # Place HL into the SP
    def ldsphl(self):
        self.r["sp"] = self.r["h"] << 8 | self.r["l"]

    # Put SP + n effective address into HL
    def ldhlspn(self):
        self.incPC()
        n = self.memory.read(self.r["pc"])

        temp = self.r["sp"] + n

        self.r["h"] = temp >> 8
        self.r["l"] = temp & 0x00FF

    # Put SP at address nn
    def ldnnsp(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])
        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        address = n1 << 8 | n2

        self.memory.write(address, self.r["sp"])

    # Push register pair AB onto stack and decrement the SP twice
    def pushnn(self, a, b):
        self.addSP(-1)
        self.memory.write(self.r["sp"], self.r[a])

        self.addSP(-1)
        self.memory.write(self.r["sp"], self.r[b])

    # Pop two byte ints off the stack increment sp twice
    def popnn(self, a, b):
        self.r[b] = self.memory.read(self.r["sp"])
        self.addSP(1)

        self.r[a] = self.memory.read(self.r["sp"])
        self.addSP(1)

    """ 8-Bit ALU Commands """

    # Add the value in reg n to A
    def addan(self, n):
        # Set the half carry flag
        self.flag["h"] = 1 if (self.r["a"] & 0x0F + self.r[n] & 0x0F) & 0x10 else 0

        self.r["a"] += self.r[n]

        # Set the final flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Add the value in memory address (HL) to A
    def addahl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])

        # Set the half carry flag
        self.flag["h"] = 1 if (self.r["a"] & 0x0F + value & 0x0F) & 0x10 else 0

        self.r["a"] += value

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Add the next memory address to A
    def addanext(self):
        self.incPC()
        value = self.memory.read(self.r["pc"])

        # Set the half carry flag
        self.flag["h"] = 1 if (self.r["a"] & 0x0F + value & 0x0F) & 0x10 else 0

        self.r["a"] += value

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0


    # Add n + carry flag to A
    def adcan(self, n):
        # Set the half carry flag
        self.flag["h"] = 1 if (self.r["a"] & 0x0F + self.r[n] & 0x0F + self.flag["c"]) & 0x10 else 0

        self.r["a"] += self.r[n] + self.flag["c"]

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Add (HL) + carry to A
    def adcahl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["h"] = 1 if (self.r["a"] & 0x0F + value & 0x0F + self.flag["c"]) & 0x10 else 0

        self.r["a"] += value + self.flag["c"]

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Add the next memory address to A + carry bit
    def adcanext(self):
        self.incPC()
        value = self.memory.read(self.r["pc"])

        self.flag["h"] = 1 if (self.r["a"] & 0x0F + value & 0x0F + self.flag["c"]) & 0x10 else 0

        self.r["a"] += value + self.flag["c"]

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Subtract register n from A
    def subn(self, n):
        self.flag["h"] = 1 if (self.r["a"] & 0x0F - self.r[n] & 0x0F) & 0x10 else 0

        self.r["a"] -= self.r[n]

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Subtract (HL) from A
    def subhl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["h"] = 1 if (self.r["a"] & 0x0F - value & 0x0F) & 0x10 else 0

        self.r["a"] -= value

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Subtract A from (PC+1)
    def subnext(self):
        self.incPC()
        value = self.memory.read(self.r["pc"])

        self.flag["h"] = 1 if (self.r["a"] & 0x0F - value & 0x0F) & 0x10 else 0

        self.r["a"] -= value

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Subtract register n + carry from A
    def sbcan(self, n):
        # Set the half carry flag
        self.flag["h"] = 1 if (self.r["a"] & 0x0F - (self.r[n] & 0x0F + self.flag["c"])) & 0x10 else 0

        self.r["a"] -= (self.r[n] + self.flag["c"])

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Subtract (HL) carry from A
    def sbcahl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["h"] = 1 if (self.r["a"] & 0x0F - (value & 0x0F + self.flag["c"])) & 0x10 else 0

        self.r["a"] -= (value + self.flag["c"])

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Subtract the next memory address value + carry from A
    def sbcanext(self):
        self.incPC()
        value = self.memory.read(self.r["pc"])

        self.flag["h"] = 1 if (self.r["a"] & 0x0F - (value & 0x0F + self.flag["c"])) & 0x10 else 0

        self.r["a"] -= (value + self.flag["c"])

        # Set the final flags
        self.flag["z"] = 0 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["a"] > 0xFFFF else 0

    # Perform A & n, place in A
    def andn(self, n):
        self.r["a"] &= self.r[n]

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 1
        self.flag["c"] = 0

    # Peform A & (HL), place in A
    def andhl(self):
        value = self.memory.load(self.r["h"] << 8 | self.r["l"])

        self.r["a"] &= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 1
        self.flag["c"] = 0

    # Perform A & (PC+1), place in A
    def andnext(self):
        self.incPC()

        value = self.memory.load(self.r["pc"])

        self.r["a"] &= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 1
        self.flag["c"] = 0

    # Perform A | n, place in A
    def orn(self, n):
        self.r["a"] |= self.r[n]

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Peform A | (HL), place in A
    def orhl(self):
        value = self.memory.load(self.r["h"] << 8 | self.r["l"])

        self.r["a"] &= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Perform A | (PC+1), place in A
    def ornext(self):
        self.incPC()

        value = self.memory.load(self.r["pc"])

        self.r["a"] ^= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Perform A ^ n, place in A
    def xorn(self, n):
        self.r["a"] |= self.r[n]

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Peform A ^ (HL), place in A
    def xorhl(self):
        value = self.memory.load(self.r["h"] << 8 | self.r["l"])

        self.r["a"] ^= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Perform A ^ (PC+1), place in A
    def xornext(self):
        self.incPC()

        value = self.memory.load(self.r["pc"])

        self.r["a"] ^= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Subtract register n from A, discard the result
    def cpn(self, n):
        self.flag["h"] = 1 if (self.r["a"] & 0x0F - self.r[n] & 0x0F) & 0x10 else 0

        discard = self.r["a"] - self.r[n]

        # Set the final flags
        self.flag["z"] = 0 if discard == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if discard > 0xFFFF else 0

    # Subtract (HL) from A, discard the result
    def cphl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["h"] = 1 if (self.r["a"] & 0x0F - value & 0x0F) & 0x10 else 0

        discard = self.r["a"] - value

        # Set the final flags
        self.flag["z"] = 0 if discard == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if discard > 0xFFFF else 0

    # Subtract A from (PC+1), dicsard result
    def cpnext(self):
        self.incPC()
        value = self.memory.read(self.r["pc"])

        self.flag["h"] = 1 if (self.r["a"] & 0x0F - value & 0x0F) & 0x10 else 0

        discard = self.r["a"] - value

        # Set the final flags
        self.flag["z"] = 0 if discard == 0 else 0
        self.flag["n"] = 0
        self.flag["c"] = 1 if discard > 0xFFFF else 0

    # Increment register n
    def incn(self, n):
        self.r[n] += 1

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 1
        self.flag["n"] = 0
        self.flag["h"] = 1 if self.r[n] & 0x10 else 0

    # Increment address value (HL)
    def inchl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"]) + 1

        # Set the flags
        self.flag["z"] = 1 if value == 0 else 1
        self.flag["n"] = 0
        self.flag["h"] = 1 if value & 0x10 else 0

        # Now write this value
        self.memory.write(self.r["h"] << 8 | self.r["l"], value)

    # Decrement register n
    def decn(self, n):
        self.r[n] -= 1

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 1
        self.flag["n"] = 0
        self.flag["h"] = 1 if self.r[n] & 0x10 else 0

    # Decrement address value (HL)
    def dechl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"]) - 1

        # Set the flags
        self.flag["z"] = 1 if value == 0 else 1
        self.flag["n"] = 0
        self.flag["h"] = 1 if value & 0x10 else 0

        # Now write this value
        self.memory.write(self.r["h"] << 8 | self.r["l"], value)

    """ 16-Bit ALU Commands """
    # Add register pair AB to HL
    def addhln(self, a, b):
        value = self.r[a] << 8 | self.r[b]
        hl = self.r["h"] << 8 | self.r["l"]

        # Set the half carry flag
        self.flag["h"] = 1 if (hl & 0x0FFF + value & 0x0FFF) & 0x1000 else 0

        final = value + hl

        # Set the remaining flags
        self.flag["n"] = 0
        self.flag["c"] = 1 if final > 0xFFFF else 0

        # Place this value in the registers
        self.r["h"] = final >> 8
        self.r["l"] = final & 0x00FF

    # Add SP to HL
    def addhlsp(self, a, b):
        hl = self.r["h"] << 8 | self.r["l"]

        # Set the half carry flag
        self.flag["h"] = 1 if (hl & 0x0FFF + self.r["sp"] & 0x0FFF) & 0x1000 else 0

        final = self.r["sp"] + hl

        # Set the remaining flags
        self.flag["n"] = 0
        self.flag["c"] = 1 if final > 0xFFFF else 0

        # Place this value in the registers
        self.r["h"] = final >> 8
        self.r["l"] = final & 0x00FF

    # Add (PC+1) to the SP
    def addspn(self):
        self.incPC()
        value = self.memory.read(self.r["pc"])

        # Set the half carry flag
        self.flag["h"] = 1 if (self.r["sp"] & 0x0FFF + value & 0x0FFF) & 0x1000 else 0

        self.r["sp"] += value

        # Set the remaining flags
        self.flag["n"] = 0
        self.flag["c"] = 1 if self.r["sp"] > 0xFFFF else 0

    # Increment the register pair AB
    def incnn(self, a, b):
        final = (self.r[a] << 8 | self.r[b]) + 1

        self.r[a] = final >> 8
        self.r[b] = final & 0x00FF

    # Increment the SP
    def incsp(self):
        self.r["sp"] += 1

    # Decrement the register pair AB
    def decnn(self, a, b):
        final = (self.r[a] << 8 | self.r[b]) - 1

        self.r[a] = final >> 8
        self.r[b] = final & 0x00FF

    # Decrement the SP
    def decsp(self):
        self.r["sp"] -= 1

    """ Miscellaneous Opcodes """
    # Swap upper and lower nibbles of n
    def swapn(self, n):
        self.r[n] = (self.r[n] & 0x0F) << 4 | self.r[n] >> 4

    # Swap upper and lower nibbles of (HL)
    def swaphl(self):
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])

        value = (value & 0x0F) << 4 | value >> 4

        self.memory.write(self.r["h"] << 8 | self.r["l"], value)

    # TODO Write this function
    def daa(self):
        pass

    # Complement the A register
    def cpl(self):
        self.r["a"] ^= 0xFF

        # Set the flags
        self.flag["n"] = 1
        self.flag["h"] = 1

    # Complement the carry flag
    def ccf(self):
        self.flag["c"] ^= 1

    # Set the carry flag
    def scf(self):
        self.flag["c"] = 1

    # No operation
    def nop(self):
        pass

    # Power down the CPU until some interrupt occurs.
    # TODO Implement this
    def halt(self):
        pass

    # Halt the CPU and display
    # TODO Implement this
    def stop(self):
        pass

    # Stop interrupts after this instruction has executed
    # TODO Implement this
    def di(self):
        pass

    # Enable interrupts after this instruction has executed
    # TODO Implement this
    def di(self):
        pass

    """ Rotate and shift instructions """
    # Rotate A left into carry flag, replace bit 0 with 7
    def rlca(self):
        bit7 = self.r["a"] & 0x80
        self.flag["c"] = bit7

        self.r["a"] <<= 1

        self.r["a"] = self.set_bit(self.r["a"], 0, bit7)

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate A left into carry flag
    def rla(self):
        self.flag["c"] = self.r["a"] & 0x80

        self.r["a"] <<= 1

         # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate A right into carry flag, replace bit 7 with 0
    def rrca(self):
        bit0 = self.r["a"] & 0x01
        self.flag["c"] = bit0

        self.r["a"] >>= 1

        self.r["a"] = self.set_bit(self.r["a"], 7, bit0)

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate A right into carry flag
    def rra(self):
        self.flag["c"] = self.r["a"] & 0x01

        self.r["a"] <<= 1

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate n left into carry flag, replace bit 0 with 7
    def rlcn(self, n):
        bit7 = self.r[n] & 0x80
        self.flag["c"] = bit7

        self.r[n] <<= 1

        self.r["a"] = self.set_bit(self.r["a"], 0, bit7)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate n left into carry flag
    def rln(self, n):
        self.flag["c"] = self.r[n] & 0x80

        self.r[n] <<= 1

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate n right into carry flag, replace bit 7 with 0
    def rrcn(self, n):
        bit0 = self.r[n] & 0x01
        self.flag["c"] = bit0

        self.r[n] >>= 1

        self.r["a"] = self.set_bit(self.r["a"], 7, bit0)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Rotate n right into carry flag
    def rra(self, n):
        self.flag["c"] = self.r[n] & 0x01

        self.r[n] <<= 1

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Shift n left into carry flag, LSB of n is set to 0
    def slan(self, n):
        self.flag["c"] = self.r[n] & 0x80

        self.r[n] <<= 1

        self.r["a"] = self.set_bit(self.r["a"], 0, 0)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Shift n right into carry, replace the MSB with the previous one?
    def sran(self, n):
        self.flag["c"] = self.r[n] & 0x01
        msb = (self.r[n] & 0x80) >> 7

        self.r[n] >>= 1

        self.r["a"] = self.set_bit(self.r["a"], 7, msb)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    # Shift n right into carry, set the msb to 0
    def srln(self, n):
        self.flag["c"] = self.r[n] & 0x01

        self.r[n] >>= 1

        self.r["a"] = self.set_bit(self.r["a"], 7, 0)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    """ Bit Opcodes """
    # Test bit b in register r
    def bitbr(self, b, r):
        # Get this bit
        bit = (self.r[r] >> (b - 1)) & 0x01

        # Set the flags
        if bit == 0:
            self.flag["z"] = 1
        self.flag["n"] = 0
        self.flag["h"] = 1

    def setbr(self, b, r):
        # Set the bit
        self.r[r] = self.set_bit(self.r[r], b, 1)

    def resbr(self, b, r):
        # Set the bit
        self.r[r] = self.set_bit(self.r[r], b, 1)

    """ Jump Operations """
    # Jump to address nn
    def jpnn(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])
        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        self.r["pc"] = n1 << 8 | n2

    # Jump to address if Z flag is reset
    def jpnznn(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])

        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        if self.flag["z"] == 0:
            self.r["pc"] = n1 << 8 | n2

    # Jump to address if Z flag is set
    def jpznn(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])

        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        if self.flag["z"] == 1:
            self.r["pc"] = n1 << 8 | n2

    # Jump to address if C flag is reset
    def jpncnn(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])

        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        if self.flag["c"] == 0:
            self.r["pc"] = n1 << 8 | n2


    # Jump to address if C flag is set
    def jpcnn(self):
        self.incPC()
        n1 = self.memory.read(self.r["pc"])

        self.incPC()
        n2 = self.memory.read(self.r["pc"])

        if self.flag["c"] == 1:
            self.r["pc"] = n1 << 8 | n2

    # Jump to the address held in HL
    def jphl(self):
        self.r["pc"] = self.r["h"] << 8 | self.r["l"]

    # Add n to current address and jump to it
    def jrn(self):
        curr = self.r["pc"]

        self.incPC()
        n = self.memory.read(self.r["pc"])

        self.r["pc"] = curr + n
        
