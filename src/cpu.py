import pygame, memory

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
	""" Function caller dictionary:
		This maps a hex int to an array, first entry being the function name, followed
		by the array of parameters """

	""" The OpcodeMap maps integers to a tuple of a function and a function paramater list """
	opmap = {
		0b0:(halt, [])
	}

	def __init__(self, memController):
		# All values are set to their initial values upon the systems startup
		self.r = { "a":0,"b":0,"c":0,"d":0red,"e":0,"f":0,"h":0,"l":0, "pc":0x100
		"sp":0xFFFE, "ime":1 }

		self.memory = memController

	""" Helper Functions """
	def setflag(self,n,val):
		mask = "0000"
		mask[n] = str(val)

		self.r["f"] = self.r["f"] | (int(mask) << 4)
		return self.r["f"]

	def getflag(self, n):
		return self.r["f"][n]

	def execute(self, pc):
		opcode = CPU.opmap[memController.read(pc)]
		opcode[0](*opcode[1]) # Execute the opcode

	# All opcode functions below

	# 8-Bit Transfer Function
	def ldr(self, r1, r2):
		self.r[r1] = self.r[r2]
		self.r["pc"]+=1

	def ldn(self, r):
		self.r[r] = read(self.r["pc"]+1)
		self.r["pc"]+=2

	def ldhl(self, r):
		self.r[r] = read((self.r["h"]<<8)|r["l"])
		self.r["pc"]+=1

	def ldhln(self):
		write((self.r["h"]<<8)|self.r["l"], read(self.r["pc"]+1))
		self.r["pc"]+=2

	def ldbc(self):
		self.r["a"] = read((self.r["b"]<<8)|r["c"])
		self.r["pc"]+=1

	def ldde(self):
		self.r["a"] = read((self.r["d"]<<8)|r["e"])
		self.r["pc"]+=1

	def ldc(self):
		self.r["a"] = read(0xFF00 | self.r["c"])
		self.r["pc"]+=1

	def lcrc(self):
		write(0xFF00 | r["c"], self.r["a"])
		self.r["pc"]+=1

	def ldan(self):
		self.r["a"] = read(self.r["pc"]+1)
		self.r["pc"]+=2

	def ldna(self):
		write(read(self.r["pc"]+1), self.r["a"])
		self.r["pc"]+=2

	def ldann(self):
		n1 = read(self.r["pc"]+1) << 8
		n2 = read(self.r["pc"]+2)

		self.r["a"] = read(n1|n2)
		self.r["pc"]+=3

	def ldnna(self):
		n1 = read(self.r["pc"]+1) << 8
		n2 = read(self.r["pc"]+2)

		write(n1|n2, self.r["a"])
		self.r["pc"]+=3

	def ldahli(self):
		hl = (self.r["h"]<<8)|self.r["l"])
		self.r["a"] = hl
		hl += 1

		self.r["h"] = hl >> 8; self.r["l"] = jl & 0xFF

		self.r["pc"]+=1

	def ldahld(self):
		hl = (self.r["h"]<<8)|self.r["l"])
		self.r["a"] = hl
		hl -= 1

		self.r["h"] = hl >> 8; self.r["l"] = jl & 0xFF

		self.r["pc"]+=1

	def ldbca(self):
		write((self.r["b"]<<8)|self.r["c"], self.r["a"])
		self.r["pc"]+=1

	def lddea(self):
		write((self.r["d"]<<8)|self.r["e"], self.r["a"])
		self.r["pc"]+=1

	def ldhlia(self):
		hl = (self.r["h"]<<8)|self.r["l"])
		write(hl, self.r["a"])
		hl += 1

		self.r["h"] = hl >> 8; self.r["l"] = jl & 0xFF

		self.r["pc"]+=1

	def ldhlda(self):
		hl = (self.r["h"]<<8)|self.r["l"])
		write(hl, self.r["a"])
		hl -= 1

		self.r["h"] = hl >> 8; self.r["l"] = jl & 0xFF

		self.r["pc"]+=1

	def ldddnn(self, d1, d2):
		self.r[d1] = read(r["pc"]+1)
		self.r[d2] = read(r["pc"]+2)

		self.r["pc"]+=3

	def ldsphl(self):
		self.r["sp"] = (self.r["h"]<<8)|self.r["l"]
		self.r["pc"]+=1

	def pushqq(self, q1, q2):
		write(self.r["sp"]-1, self.r[q1])
		write(self.r["sp"]-2, self.r[q2])

		self.r["sp"] -= 2
		self.r["pc"] += 1

	def popqq(self, q1, q2):
		self.r[q1] = read(self.r["sp"])
		self.r[q2] = read(self.r["sp"]+1)

		self.r["sp"] += 2
		self.r["pc"] += 1

	def ldhlspe(self):
		e = read(self.r["pc"]+1)

		if e & 0x80:
			e -= 0x100

		hl = self.r["sp"] + e

		if e >= 0:
			setflag(2, ((self.r["sp"] & 0xF) + (e & 0xF)) > 0xF)
			setflag(3, ((self.r["sp"] & 0xFF) + e) > 0xFF)
		else:
			setflag(2, (self.r["sp"] & 0xFF) <= (hl & 0xFF))
			setflag(3, (self.r["sp"] & 0xF) <= (hl & 0xF))

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xF

	def ldnnsp(self):
		nn = (read(self.r["pc"]+1)<<8) | read(self.r["pc"]+2)
		write(nn, self.r["sp"]&0xFF)
		write(nn+1, self.r["sp"]>>8)

		self.r["pc"]+=3

	def add(self, val, pc):
		temp = self.r["a"]
		self.r["a"] += val

		# Set if zero
		setflag(0, self.r["a"] == 0)
		# Reset subtration bit
		setflag(1, 0)
		# Check for carry from 4th to 5th bit
		setflag(2, ((temp&0xF)+(val&0xF) > 0xF))
		# Check for overflow
		setflag(3, self.r["a"] > 0xFF)

		self.r["pc"] += pc

	def adc(self, var, pc):
		temp = self.r["a"]
		self.r["a"] += val + getflag(3)

		# Set if zero
		setflag(0, self.r["a"] == 0)
		# Reset subtration bit
		setflag(1, 0)
		# Check for carry from 4th to 5th bit
		setflag(2, ((temp&0xF)+(val&0xF)+getflag(3) > 0xF))
		# Check for overflow
		setflag(3, self.r["a"] > 0xFF)

		self.r["pc"] += pc

	def sub(self, val, pc):
		temp = self.r["a"]
		self.r["a"] -= val

		# Set if zero
		setflag(0, self.r["a"] == 0)
		# Reset subtration bit
		setflag(1, 0)

		setflag(2, (self.r["a"] & 0xF) <= (temp & 0xF))

		setflag(3, (self.r["a"] & 0xFF) <= (temp & 0xFF))

		self.r["pc"] += pc

	def subc(self, var, pc):
		temp = self.r["a"]
		self.r["a"] -= (val-getflag(3))

		# Set if zero
		setflag(0, self.r["a"] == 0)
		# Reset subtration bit
		setflag(1, 0)

		setflag(2, (self.r["a"] & 0xF) <= (temp & 0xF))

		setflag(3, (self.r["a"] & 0xFF) <= (temp & 0xFF))

		self.r["pc"] += pc

	def gband(self, var, pc):
		self.r["a"] &= var

		setflag(0, self.r["a"] == 0)
		setflag(1, 0)
		setflag(2, 1)
		setflag(3, 0)

		self.r["pc"] += pc

	def gbor(self, var, pc):
		self.r["a"] |= var

		setflag(0, self.r["a"] == 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, 0)

		self.r["pc"] += pc

	def xor(self, var, pc):
		self.r["a"] ^= var

		setflag(0, self.r["a"] == 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, 0)

		self.r["pc"] += pc

	def cpn(self, var, pc):
		setflag(0, self.r["a"] == var)
		setflag(1, 1)
		setflag(2, (self.r["a"] & 0xF) <= (var & 0xF))
		setflag(3, self.r["a"] < var)

		self.r["pc"] += pc

	def inc(self, r):
		self.r[r] += 1
		setflag(0, self.r["a"] == 0)
		setflag(1, 0)
		setflag(2, ((self.r[r]-1) & 0xF) + 1 > 0xF)

		self.r["pc"] += 1

	def inchl(self):
		hl = (self.r["h"]<<8)|self.r["l"]

		hl += 1

		setflag(0, hl == 0)
		setflag(1, 0)
		setflag(2, ((hl-1) & 0xF) + 1 > 0xF)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xF

		self.r["pc"] += 1

	def dec(self, r):
		self.r[r] -= 1
		setflag(0, self.r["a"] == 0)
		setflag(1, 1)
		setflag(2, ((self.r[r]+1) & 0xF) - 1 > 0xF)

		self.r["pc"] += 1

	def dechl(self):
		hl = (self.r["h"]<<8)|self.r["l"]

		hl -= 1

		setflag(0, hl == 0)
		setflag(1, 1)
		setflag(2, ((hl+1) & 0xF) - 1 > 0xF)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xF

		self.r["pc"] += 1

	def addhlss(self, a, b):
		hl = (self.r["h"] << 8) | self.r["l"]
		reg = (self.r[a] << 8) | self.r[b]

		setflag(1, 0)
		setflag(2, (hl&0xF) + (reg&0xF) > 0xF)
		setflag(3, (hl&0XFF) + (reg&0xFF) > 0xFF)

		hl += reg
		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1

	def addspe(self):
		e = read(self.r["pc"]+1)

		# First bit is set
		if e & 0x80:
			e -= 0x100

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, (self.r["sp"]&0xF) + e & 0xF > 0xF)
		setflag(3, (self.r["sp"]&0xFF) + e > 0xFF)

		self.r["sp"] += e

		self.r["pc"] += 2

	def incss(self, a, b):
		reg = (self.[a] << 8) | self.r[b]

		reg += 1

		self.r[a] = reg >> 8
		self.r[b] = reg & 0xF

		self.r["pc"] += 1

	def decss(self, a, b):
		reg = (self.[a] << 8) | self.r[b]

		reg -= 1

		self.r[a] = reg >> 8
		self.r[b] = reg & 0xF

		self.r["pc"] += 1

	def rlca(self):
		bit = self.r["a"] & 0x80

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["a"] = (self.r["a"] << 1) & 0xFF

		self.r["pc"]+=1

	def rla(self):
		self.r["a"] <<= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, self.r["a"] & 0x80)

		self.r["pc"] += 1

	def rrca(self):
		bit = self.r["a"] & 0x1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["a"] >>= 1

		self.r["pc"] += 1

	def rra(self):
		self.r["a"] >>= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, self.r["a"] & 0x1)

		self.r["pc"] += 1

	def rlcm(self, m):
		bit = self.r[m] & 0x80

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r[m] = (self.r[m] << 1) & 0xFF

		self.r["pc"]+=1

	def rlchl(self):
		hl = (self.r["h"] << 8) | self.r["l"]

		bit = hl & 0x80

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		hl = (hl << 1) & 0xFFFF

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1

	def rlm(self, m):
		self.r[m] = (self.r[m] << 1) & 0xFF

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, self.r[m] & 0x80)

		self.r["pc"]+=1

	def rlhl(self):
		hl = (self.r["h"] << 8) | self.r["l"]

		hl = (hl << 1) & 0xFFFF

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, hl & 0x80)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"]+=1

	def rrcm(self, m):
		bit = self.r[m] & 0x1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r[m] >>= 1

		self.r["pc"] += 1

	def rrchl(self):
		hl = (self.r["h"] << 8) | self.r["l"]

		bit = hl & 0x1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		hl >>= 1

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1

	def rrm(self, m):
		self.r[m] >>= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, self.r[m] & 0x1)

		self.r["pc"] += 1

	def rrhl(self):
		hl = (self.r["h"] << 8) | self.r["l"]

		hl >>= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, hl & 0x1)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1

	def slam(self, m):
		bit = self.r[m] & 0x80

		self.r[m] <<= 1
		self.r[m] &= 0xFE # Set bit 0

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["pc"] += 1

	def slahl(self):
		hl = (self.r["h"] << 8) | self.r["l"]
		bit = hl & 0x80

		hl <<= 1
		hl &= 0xFFFE # Set bit 0

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1

	def sram(self, m):
		bit = self.r[m] & 0x80

		self.r[m] >>= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["pc"] += 1

	def srahl(self):
		hl = (self.r["h"] << 8) | self.r["l"]
		bit = hl & 0x1

		hl >>= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1

	def srlm(self, m):
		bit = self.r[m] & 0x1

		self.r[m] >>= 1
		self.r[m] &= 0x7F

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["pc"] += 1

	def srlhl(self):
		hl = (self.r["h"] << 8) | self.r["l"]
		bit = hl & 0x80

		hl >>= 1

		setflag(0, 0)
		setflag(1, 0)
		setflag(2, 0)
		setflag(3, bit)

		self.r["h"] = hl >> 8
		self.r["l"] = hl & 0xFF

		self.r["pc"] += 1