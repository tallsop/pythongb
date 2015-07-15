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
            "z": 0,
            "n": 0,
            "h": 0,
            "c": 0
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

    def pushpc(self):
        self.addSP(-1)
        self.memory.write(self.r["sp"], self.r["pc"] >> 8)

        self.addSP(-1)
        self.memory.write(self.r["sp"], self.r["pc"] & 0x00FF)

    """ Opcode functions are below """

    """ All 8-Bit load functions """
    # Place the value n into nn
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

        self.r["a"] = self.memory.read(n2 << 8 | n1)

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
    def ldnna(self):
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

        self.r[a] = n2
        self.r[b] = n1

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
        self.memory.write(self.r["pc"], self.r["sp"] & 0x00FF)

        self.incPC()
        self.memory.write(self.r["pc"], self.r["sp"] >> 8)

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
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])

        self.r["a"] &= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 1
        self.flag["c"] = 0

    # Perform A & (PC+1), place in A
    def andnext(self):
        self.incPC()

        value = self.memory.read(self.r["pc"])

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
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])

        self.r["a"] &= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Perform A | (PC+1), place in A
    def ornext(self):
        self.incPC()

        value = self.memory.read(self.r["pc"])

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
        value = self.memory.read(self.r["h"] << 8 | self.r["l"])

        self.r["a"] ^= value

        # Set the flags
        self.flag["z"] = 1 if self.r["a"] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0
        self.flag["c"] = 0

    # Perform A ^ (PC+1), place in A
    def xornext(self):
        self.incPC()

        value = self.memory.read(self.r["pc"])

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
    def ei(self):
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

        self.r["n"] = self.set_bit(self.r["n"], 0, bit7)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def rlchl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])

        bit7 = hl & 0x80
        self.flag["c"] = bit7

        hl <<= 1

        hl = self.set_bit(hl, 0, bit7)

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)

    # Rotate n left into carry flag
    def rln(self, n):
        self.flag["c"] = self.r[n] & 0x80

        self.r[n] <<= 1

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def rlhl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["c"] = hl & 0x80

        hl <<= 1

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)

    # Rotate n right into carry flag, replace bit 7 with 0
    def rrcn(self, n):
        bit0 = self.r[n] & 0x01
        self.flag["c"] = bit0

        self.r[n] >>= 1

        self.r[n] = self.set_bit(self.r[n], 7, bit0)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def rrchl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])
        bit0 = hl & 0x01
        self.flag["c"] = bit0

        hl >>= 1

        hl = self.set_bit(hl, 7, bit0)

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)

    # Rotate n right into carry flag
    def rrn(self, n):
        self.flag["c"] = self.r[n] & 0x01

        self.r[n] <<= 1

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def rrhl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["c"] = hl & 0x01

        hl <<= 1

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)


    # Shift n left into carry flag, LSB of n is set to 0
    def slan(self, n):
        self.flag["c"] = self.r[n] & 0x80

        self.r[n] <<= 1

        self.r[n] = self.set_bit(self.r[n], 0, 0)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def slahl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["c"] = hl & 0x80

        hl <<= 1

        hl = self.set_bit(hl, 0, 0)

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)


    # Shift n right into carry, replace the MSB with the previous one?
    def sran(self, n):
        self.flag["c"] = self.r[n] & 0x01
        msb = (self.r[n] & 0x80) >> 7

        self.r[n] >>= 1

        self.r[n] = self.set_bit(self.r[n], 7, msb)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def srahl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["c"] = hl & 0x01
        msb = (hl & 0x80) >> 7

        hl >>= 1

        hl = self.set_bit(hl, 7, msb)

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)

    # Shift n right into carry, set the msb to 0
    def srln(self, n):
        self.flag["c"] = self.r[n] & 0x01

        self.r[n] >>= 1

        self.r[n] = self.set_bit(self.r[n], 7, 0)

        # Set the flags
        self.flag["z"] = 1 if self.r[n] == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

    def srlhl(self):
        hl = self.memory.read(self.r["h"] << 8 | self.r["l"])
        self.flag["c"] = hl & 0x01

        hl >>= 1

        hl = self.set_bit(hl, 7, 0)

        # Set the flags
        self.flag["z"] = 1 if hl == 0 else 0
        self.flag["n"] = 0
        self.flag["h"] = 0

        self.memory.write(self.r["h"] << 8 | self.r["l"], hl)

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
        self.r[r] = self.set_bit(self.r[r], b, 0)

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

    # If Z is reset, jump to current address + n
    def jrnzn(self):
        self.incPC()
        if self.flag["z"] == 0:
            n = self.memory.read(self.r["pc"])
            self.r["pc"] += n - 1

    # If Z is set, jump to current address + n
    def jrzn(self):
        self.incPC()
        if self.flag["z"] == 1:
            n = self.memory.read(self.r["pc"])
            self.r["pc"] += n - 1

    def jrncn(self):
        self.incPC()
        if self.flag["c"] == 0:
            n = self.memory.read(self.r["pc"])
            self.r["pc"] += n - 1

    def jrcn(self):
        self.incPC()
        if self.flag["c"] == 1:
            n = self.memory.read(self.r["pc"])
            self.r["pc"] += n - 1

    """ Function Call Opcodes """
    # Push address of next instruction onto the stack then go to nn
    def callnn(self):
        # Push the pc to the stack
        self.pushpc()

        self.incPC()
        low = self.memory.read(self.r["pc"])

        self.incPC()
        high = self.memory.read(self.r["pc"])

        self.r["pc"] = high << 8 | low

    # Call the address nn if the Z flag is reset
    def callnznn(self):
        if self.flag["z"] == 0:
            # Push the pc to the stack
            self.pushpc()

            self.incPC()
            low = self.memory.read(self.r["pc"])

            self.incPC()
            high = self.memory.read(self.r["pc"])

            self.r["pc"] = high << 8 | low

        else:
            self.incPC()
            self.incPC()

    # Call the address nn if the Z flag is set
    def callznn(self):
        if self.flag["z"] == 1:
            # Push the pc to the stack
            self.pushpc()

            self.incPC()
            low = self.memory.read(self.r["pc"])

            self.incPC()
            high = self.memory.read(self.r["pc"])

            self.r["pc"] = high << 8 | low

        else:
            self.incPC()
            self.incPC()

    # Call the address nn if the c flag is reset
    def callncnn(self):
        if self.flag["c"] == 0:
            # Push the pc to the stack
            self.pushpc()

            self.incPC()
            low = self.memory.read(self.r["pc"])

            self.incPC()
            high = self.memory.read(self.r["pc"])

            self.r["pc"] = high << 8 | low

        else:
            self.incPC()
            self.incPC()

    # Call the address nn if the c flag is set
    def callcnn(self):
        if self.flag["c"] == 1:
            # Push the pc to the stack
            self.pushpc()

            self.incPC()
            low = self.memory.read(self.r["pc"])

            self.incPC()
            high = self.memory.read(self.r["pc"])

            self.r["pc"] = high << 8 | low

        else:
            self.incPC()
            self.incPC()

    """ Restart Opcodes """
    # Push the current address onto the stack and jump to address 0x0000 + n
    def rstn(self, n):
        self.pushpc()
        self.r["pc"] = 0x0000 + n


    """ Return Opcodes """
    # Pop two bytes off the stack and jump to that address
    def ret(self):
        low = self.memory.read(self.r["sp"])
        self.addSP(1)
        high = self.memory.read(self.r["sp"])
        self.addSP(1)

        self.r["pc"] = high << 8 | low

    # Return if the Z flag is reset
    def retnz(self):
        if self.flag["z"] == 0:
            low = self.memory.read(self.r["sp"])
            self.addSP(1)
            high = self.memory.read(self.r["sp"])
            self.addSP(1)

            self.r["pc"] = high << 8 | low

    # Return if the Z flag is set
    def retz(self):
        if self.flag["z"] == 1:
            low = self.memory.read(self.r["sp"])
            self.addSP(1)
            high = self.memory.read(self.r["sp"])
            self.addSP(1)

            self.r["pc"] = high << 8 | low

    # Return if the C flag is reset
    def retnc(self):
        if self.flag["C"] == 0:
            low = self.memory.read(self.r["sp"])
            self.addSP(1)
            high = self.memory.read(self.r["sp"])
            self.addSP(1)

            self.r["pc"] = high << 8 | low

    # Return if the C flag is set
    def retnc(self):
        if self.flag["C"] == 1:
            low = self.memory.read(self.r["sp"])
            self.addSP(1)
            high = self.memory.read(self.r["sp"])
            self.addSP(1)

            self.r["pc"] = high << 8 | low

    # Pop two bytes off the stack and enable interrupts
    def reti(self):
        low = self.memory.read(self.r["sp"])
        self.addSP(1)
        high = self.memory.read(self.r["sp"])
        self.addSP(1)

        self.r["pc"] = high << 8 | low

        # TODO: Enable interrupts

    def cbtable(self, opcode):
        self.incPC()

        lookup = {
            # SWAP n
            0x37: (self.swapn, ["a"]),
            0x30: (self.swapn, ["b"]),
            0x31: (self.swapn, ["c"]),
            0x32: (self.swapn, ["d"]),
            0x33: (self.swapn, ["e"]),
            0x34: (self.swapn, ["h"]),
            0x35: (self.swapn, ["l"]),
            0x36: (self.swaphl, []),

            # RLC n
            0x07: (self.rlcn, ["a"]),
            0x00: (self.rlcn, ["b"]),
            0x01: (self.rlcn, ["c"]),
            0x02: (self.rlcn, ["d"]),
            0x03: (self.rlcn, ["e"]),
            0x04: (self.rlcn, ["h"]),
            0x05: (self.rlcn, ["l"]),
            0x06: (self.rlchl, []),

            # RL n
            0x17: (self.rln, ["a"]),
            0x10: (self.rln, ["b"]),
            0x11: (self.rln, ["c"]),
            0x12: (self.rln, ["d"]),
            0x13: (self.rln, ["e"]),
            0x14: (self.rln, ["h"]),
            0x15: (self.rln, ["l"]),
            0x16: (self.rlhl, []),

            # RRC n
            0x0F: (self.rrcn, ["a"]),
            0x08: (self.rrcn, ["b"]),
            0x09: (self.rrcn, ["c"]),
            0x0A: (self.rrcn, ["d"]),
            0x0B: (self.rrcn, ["e"]),
            0x0C: (self.rrcn, ["h"]),
            0x0D: (self.rrcn, ["l"]),
            0x0E: (self.rrchl, []),

            # RR n
            0x1F: (self.rrn, ["a"]),
            0x18: (self.rrn, ["b"]),
            0x19: (self.rrn, ["c"]),
            0x1A: (self.rrn, ["d"]),
            0x1B: (self.rrn, ["e"]),
            0x1C: (self.rrn, ["h"]),
            0x1D: (self.rrn, ["l"]),
            0x1E: (self.rrhl, []),

            # SLA n
            0x27: (self.slan, ["a"]),
            0x20: (self.slan, ["b"]),
            0x21: (self.slan, ["c"]),
            0x22: (self.slan, ["d"]),
            0x23: (self.slan, ["e"]),
            0x24: (self.slan, ["h"]),
            0x25: (self.slan, ["l"]),
            0x26: (self.slahl, []),

            # SRA n
            0x2F: (self.sran, ["a"]),
            0x28: (self.sran, ["b"]),
            0x29: (self.sran, ["c"]),
            0x2A: (self.sran, ["d"]),
            0x2B: (self.sran, ["e"]),
            0x2C: (self.sran, ["h"]),
            0x2D: (self.sran, ["l"]),
            0x2E: (self.srahl, []),

            # SRL n
            0x3F: (self.srln, ["a"]),
            0x38: (self.srln, ["b"]),
            0x39: (self.srln, ["c"]),
            0x3A: (self.srln, ["d"]),
            0x3B: (self.srln, ["e"]),
            0x3C: (self.srln, ["h"]),
            0x3D: (self.srln, ["l"]),
            0x3E: (self.srahl, []),

            # BIT/SET/RES b,r (unimplemented)
        }

        function = lookup[opcode]

        function[0](*function[1])

    # Opcode Maps
    def executeOpcode(self, opcode):
        map = {
            # LD nn, n
            0x06: (self.ldnnn, ["b"]),
            0x0E: (self.ldnnn, ["c"]),
            0x16: (self.ldnnn, ["d"]),
            0x1E: (self.ldnnn, ["e"]),
            0x26: (self.ldnnn, ["h"]),
            0x2E: (self.ldnnn, ["l"]),

            # LD r1, r2
            0x7F: (self.ldr1r2, ["a", "a"]),
            0x78: (self.ldr1r2, ["a", "b"]),
            0x79: (self.ldr1r2, ["a", "c"]),
            0x7A: (self.ldr1r2, ["a", "d"]),
            0x7B: (self.ldr1r2, ["a", "e"]),
            0x7C: (self.ldr1r2, ["a", "h"]),
            0x7D: (self.ldr1r2, ["a", "l"]),
            0x7E: (self.ldr1hl, ["a"]),
            0x40: (self.ldr1r2, ["b", "b"]),
            0x41: (self.ldr1r2, ["b", "c"]),
            0x42: (self.ldr1r2, ["b", "d"]),
            0x43: (self.ldr1r2, ["b", "e"]),
            0x44: (self.ldr1r2, ["b", "h"]),
            0x45: (self.ldr1r2, ["b", "l"]),
            0x46: (self.ldr1hl, ["b"]),
            0x48: (self.ldr1r2, ["c", "b"]),
            0x49: (self.ldr1r2, ["c", "c"]),
            0x4A: (self.ldr1r2, ["c", "d"]),
            0x4B: (self.ldr1r2, ["c", "e"]),
            0x4C: (self.ldr1r2, ["c", "h"]),
            0x4D: (self.ldr1r2, ["c", "l"]),
            0x4E: (self.ldr1hl, ["c"]),
            0x50: (self.ldr1r2, ["d", "b"]),
            0x51: (self.ldr1r2, ["d", "c"]),
            0x52: (self.ldr1r2, ["d", "d"]),
            0x53: (self.ldr1r2, ["d", "e"]),
            0x54: (self.ldr1r2, ["d", "h"]),
            0x55: (self.ldr1r2, ["d", "l"]),
            0x56: (self.ldr1hl, ["d"]),
            0x58: (self.ldr1r2, ["e", "b"]),
            0x59: (self.ldr1r2, ["e", "c"]),
            0x5A: (self.ldr1r2, ["e", "d"]),
            0x5B: (self.ldr1r2, ["e", "e"]),
            0x5C: (self.ldr1r2, ["e", "h"]),
            0x5D: (self.ldr1r2, ["e", "l"]),
            0x5E: (self.ldr1hl, ["e"]),
            0x60: (self.ldr1r2, ["h", "b"]),
            0x61: (self.ldr1r2, ["h", "c"]),
            0x62: (self.ldr1r2, ["h", "d"]),
            0x63: (self.ldr1r2, ["h", "e"]),
            0x64: (self.ldr1r2, ["h", "h"]),
            0x65: (self.ldr1r2, ["h", "l"]),
            0x66: (self.ldr1hl, ["h"]),
            0x68: (self.ldr1r2, ["l", "b"]),
            0x69: (self.ldr1r2, ["l", "c"]),
            0x6A: (self.ldr1r2, ["l", "d"]),
            0x6B: (self.ldr1r2, ["l", "e"]),
            0x6C: (self.ldr1r2, ["l", "h"]),
            0x6D: (self.ldr1r2, ["l", "l"]),
            0x6E: (self.ldr1hl, ["l"]),
            0x70: (self.ldhlr2, ["b"]),
            0x71: (self.ldhlr2, ["c"]),
            0x72: (self.ldhlr2, ["d"]),
            0x73: (self.ldhlr2, ["e"]),
            0x74: (self.ldhlr2, ["h"]),
            0x75: (self.ldhlr2, ["l"]),
            0x36: (self.ldhln, []),

            # LD A, n
            0x0A: (self.ldab, ["b", "c"]),
            0x1A: (self.ldab, ["d", "e"]),
            0xFA: (self.ldann, []),
            0x3E: (self.ldae, []),

            # LD n, A
            0x47: (self.ldna, ["b"]),
            0x4F: (self.ldna, ["c"]),
            0x57: (self.ldna, ["d"]),
            0x5F: (self.ldna, ["e"]),
            0x67: (self.ldna, ["h"]),
            0x6F: (self.ldna, ["l"]),
            0x02: (self.ldaba, ["b", "c"]),
            0x12: (self.ldaba, ["d", "e"]),
            0x77: (self.ldaba, ["h", "l"]),
            0xEA: (self.ldnna, []),

            # LD A,(C)
            0xF2: (self.ldac, []),

            # LD (C), A
            0xE2: (self.ldca, []),

            # LDD A, (HL)
            0x3A: (self.lddahl, []),

            # LDD (HL), A
            0x32: (self.lddhla, []),

            # LDI A, (HL)
            0x2A: (self.ldiahl, []),

            # LDI (HL), A
            0x22: (self.ldihla, []),

            # LDH (n), A
            0xE0: (self.ldhan, []),

            # LDH A, (n)
            0xF0: (self.ldhan, []),

            # LD n, nn
            0x01: (self.ldnnn16, ["b", "c"]),
            0x11: (self.ldnnn16, ["d", "e"]),
            0x21: (self.ldnnn16, ["h", "l"]),
            0x31: (self.ldnnsp, []),

            # LD SP, HL
            0xF9: (self.ldsphl, []),

            # LDHL SP, n
            0xF8: (self.ldhlspn, []),

            # LD (nn), SP
            0x08: (self.ldnnsp, []),

            # PUSH nn
            0xF5: (self.pushnn, ["a", "f"]),
            0xC5: (self.pushnn, ["b", "c"]),
            0xD5: (self.pushnn, ["d", "e"]),
            0xE5: (self.pushnn, ["h", "l"]),

            # POP nn
            0xF1: (self.popnn, ["a", "f"]),
            0xC1: (self.popnn, ["b", "c"]),
            0xD1: (self.popnn, ["d", "e"]),
            0xE1: (self.popnn, ["h", "l"]),

            # ADD A, n
            0x87: (self.addan, ["a"]),
            0x80: (self.addan, ["b"]),
            0x81: (self.addan, ["c"]),
            0x82: (self.addan, ["d"]),
            0x83: (self.addan, ["e"]),
            0x84: (self.addan, ["h"]),
            0x85: (self.addan, ["l"]),
            0x86: (self.addahl, []),
            0xC6: (self.addanext, []),

            # ADC A, n
            0x8F: (self.adcan, ["a"]),
            0x88: (self.adcan, ["b"]),
            0x89: (self.adcan, ["c"]),
            0x8A: (self.adcan, ["d"]),
            0x8B: (self.adcan, ["e"]),
            0x8C: (self.adcan, ["h"]),
            0x8D: (self.adcan, ["l"]),
            0x8E: (self.adcahl, []),
            0xCE: (self.adcanext, []),

            # SUB n
            0x97: (self.subn, ["a"]),
            0x90: (self.subn, ["b"]),
            0x91: (self.subn, ["c"]),
            0x92: (self.subn, ["d"]),
            0x93: (self.subn, ["e"]),
            0x94: (self.subn, ["h"]),
            0x95: (self.subn, ["l"]),
            0x96: (self.subhl, []),
            0xD6: (self.subnext, []),

            # SBC A, n
            0x9F: (self.sbcan, ["a"]),
            0x98: (self.sbcan, ["b"]),
            0x99: (self.sbcan, ["c"]),
            0x9A: (self.sbcan, ["d"]),
            0x9B: (self.sbcan, ["e"]),
            0x9C: (self.sbcan, ["h"]),
            0x9D: (self.sbcan, ["l"]),
            0x9E: (self.sbcahl, []),

            # AND n
            0xA7: (self.andn, ["a"]),
            0xA0: (self.andn, ["b"]),
            0xA1: (self.andn, ["c"]),
            0xA2: (self.andn, ["d"]),
            0xA3: (self.andn, ["e"]),
            0xA4: (self.andn, ["h"]),
            0xA5: (self.andn, ["l"]),
            0xA6: (self.andhl, []),
            0xE6: (self.andnext, []),

            # OR n
            0xB7: (self.orn, ["a"]),
            0xB0: (self.orn, ["b"]),
            0xB1: (self.orn, ["c"]),
            0xB2: (self.orn, ["d"]),
            0xB3: (self.orn, ["e"]),
            0xB4: (self.orn, ["h"]),
            0xB5: (self.orn, ["l"]),
            0xB6: (self.orhl, []),
            0xF6: (self.ornext, []),

            # XOR n
            0xAF: (self.xorn, ["a"]),
            0xA8: (self.xorn, ["b"]),
            0xA9: (self.xorn, ["c"]),
            0xAA: (self.xorn, ["d"]),
            0xAB: (self.xorn, ["e"]),
            0xAC: (self.xorn, ["h"]),
            0xAD: (self.xorn, ["l"]),
            0xAE: (self.xorhl, []),
            0xEE: (self.xornext, []),

            # CP n
            0xBF: (self.cpn, ["a"]),
            0xB8: (self.cpn, ["b"]),
            0xB9: (self.cpn, ["c"]),
            0xBA: (self.cpn, ["d"]),
            0xBB: (self.cpn, ["e"]),
            0xBC: (self.cpn, ["h"]),
            0xBD: (self.cpn, ["l"]),
            0xBE: (self.cphl, []),
            0xFE: (self.cpnext, []),

            # INC n
            0x3C: (self.incn, ["a"]),
            0x04: (self.incn, ["b"]),
            0x0C: (self.incn, ["c"]),
            0x14: (self.incn, ["d"]),
            0x1C: (self.incn, ["e"]),
            0x24: (self.incn, ["h"]),
            0x2C: (self.incn, ["l"]),
            0x34: (self.inchl, []),

            # DEC n
            0x3D: (self.decn, ["a"]),
            0x05: (self.decn, ["b"]),
            0x0D: (self.decn, ["c"]),
            0x15: (self.decn, ["d"]),
            0x1D: (self.decn, ["e"]),
            0x25: (self.decn, ["h"]),
            0x2D: (self.decn, ["l"]),
            0x35: (self.dechl, []),

            # ADD HL, n
            0x09: (self.addhln, ["b", "c"]),
            0x19: (self.addhln, ["d", "e"]),
            0x29: (self.addhln, ["h", "l"]),
            0x39: (self.addhlsp, []),

            # ADD SP, n
            0xE8: (self.addspn, []),

            # INC nn
            0x03: (self.incnn, ["b", "c"]),
            0x13: (self.incnn, ["d", "e"]),
            0x23: (self.incnn, ["h", "l"]),
            0x33: (self.incsp, []),

            # DEC nn
            0x0B: (self.decnn, ["b", "c"]),
            0x1B: (self.decnn, ["d", "e"]),
            0x2B: (self.decnn, ["h", "l"]),
            0x3B: (self.decsp, []),

            # SWAP n
            # RLC n
            # RL n
            0xCB: (self.cbtable, []),

            # DAA
            0x27: (self.daa, []),

            # CPL
            0x2F: (self.cpl, []),

            # CCF
            0x3F: (self.ccf, []),

            # SCF
            0x37: (self.scf, []),

            # NOP
            0x00: (self.nop, []),

            # HALT
            0x76: (self.halt, []),

            # STOP
            0x10: (self.stop, []),

            # DI
            0xF3: (self.di, []),

            # EI
            0xFB: (self.ei, []),

            # RLCA
            0x07: (self.rlca, []),

            # RLA
            0x17: (self.rla, []),

            # RRCA
            0x0F: (self.rrca, []),

            # RRA
            0x1F: (self.rra, []),

            # JP nn
            0xC3: (self.jpnn, []),

            # JP cc, nn
            0xC2: (self.jpnznn, []),
            0xCA: (self.jpznn, []),
            0xD2: (self.jpncnn, []),
            0xDA: (self.jpcnn, []),

            # JP (HL)
            0xE9: (self.jphl, []),

            # JR n
            0x18: (self.jrn, []),

            # JR cc, n
            0x20: (self.jrnzn, []),
            0x28: (self.jrzn, []),
            0x30: (self.jrncn, []),
            0x38: (self.jrcn, []),

            # CALL nn
            0xCD: (self.callnn, []),

            # CALL cc, nn
            0xC4: (self.callnznn, []),
            0xCC: (self.callznn, []),
            0xD4: (self.callncnn, []),
            0xDC: (self.callcnn, []),

            # RST n
            0xC7: (self.rstn, [0x00]),
            0xCF: (self.rstn, [0x08]),
            0xD7: (self.rstn, [0x10]),
            0xDF: (self.rstn, [0x18]),
            0xE7: (self.rstn, [0x20]),
            0xEF: (self.rstn, [0x28]),
            0xF7: (self.rstn, [0x30]),
            0xFF: (self.rstn, [0x38]),

            # RET
            0xC9: (self.ret, []),

            # RET cc
            0xC0: (self.retnz, []),
            0xC8: (self.retz, []),
            0xD0: (self.retnc, []),
            0xD8: (self.retc, []),

            # RETI
            0xD9: (self.reti, [])
        }

        function = map[opcode]
        function[0](*function[1])


