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
	# Bytes in opcode which refer to register
	byteRegMap = { 0b111:"a", 0b000:"b", 0b001:"c", 0b010:"d", 0b011:"e", 0b100:"h", 0b101:"l" }

	pairMap = { 0b00:"bc", 0b01:"de", 0b10:"hl", 0b11:"sp" }

	# Refers to values you can place in setflag function
	flagMap = { 0b00:[0,0], 0b01:[0,1], 0b10:[3,0], 0b11:[3,0] }

	# Refers to value in the RST t function
	tMap = { 0:0x00, 1:0x08, 2:0x10, 3:0x18, 4:0x20, 5:0x28, 6:0x30, 7:0x38 }

	# All values are set to their initial values upon the systems startup
	def __init__(self, memController):
		self.clock = 0
		self.pc = 0x100
		self.r = { "a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"h":0,"l":0,
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

	def add(self,a,b):
		res = a + b

		# Set if zero
		setflag(0, res == 0)
		# Reset subtration bit
		setflag(1, 0)
		# Check for carry from 4th to 5th bit
		setflag(2, ((a&0xF)+(b&0xF) > 0xF))
		# Check for overflow
		setflag(3, res > 0xFF)

		return res

	def execute(self):
		cycles = 0

		opcode = self.memory.read(self.pc)

		""" 
		Here is where opcodes are executed in the order of the Game Boy manual with exceptions where
		the masking of an opcode causes the wrong one to be executed, in these cases, the exact opcode
		copy is placed above the one which is causing problems.
		"""
		if opcode & 0b11000000 == 0b01000000:
			t = opcode & 0b00111111
			self.r[CPU.byteRegMap[t>>3]] = self.r[CPU.byteRegMap[t&0b00000111]]
			self.pc+=1; cycles=1

		elif opcode & 0b11000111 == 0b00000110:
			t = self.memory.read(self.pc+1)
			self.r[CPU.byteRegMap[(opcode&0b00111000)>>3]] = t
			self.pc+=2; cycles=2

		elif opcode & 0b11000111 == 0b01000110:
			self.r[CPU.byteRegMap[(opcode&0b00111000)>>3]] = read((self.r["h"] << 8) | self.r["l"])
			self.pc+=1; cycles=2

		elif opcode & 0b11111000 == 0b01110000:
			t = h[CPU.byteRegMap[opcode&0b00000111]]
			self.memory.write((self.r["h"] << 8) | self.r["l"], t)
			self.pc+=1; cycles=2

		elif opcode == 0b00110110:
			n = self.memory.read(self.pc+1)
			self.memory.write((self.r["h"] << 8) | self.r["l"], n)
			self.pc+=2; cycles=3

		elif opcode == 0b00001010:
			self.r["a"] = read((self.r["b"] << 8) | self.r["c"])
			self.pc+=1; cycles=2

		elif opcode == 0b00011010:
			self.r["a"] = read((self.r["d"] << 8) | self.r["e"])
			self.pc+=1; cycles=2

		elif opcode == 0b11110010:
			self.r["a"] = self.memory.read(0xFF00 + self.r["c"])
			self.pc+=1; cycles=2

		elif opcode == 0b11100010:
			self.memory.write(0xFF00 + self.r["c"], self.r["a"])
			self.pc+=1; cycles=2

		elif opcode == 0b11110000:
			n = self.memory.read(self.pc+1)
			self.r["a"] = self.memory.read(n)
			self.pc+=2; cycles=3

		elif opcode == 0b11100000:
			n = self.memory.read(self.pc+1)
			self.memory.write(n, self.r["a"])
			self.pc+=2; cycles=3

		elif opcode == 0b11111010:
			n1 = self.memory.read(self.pc+1)
			n2 = self.memory.read(self.pc+2)
			self.r["a"]= self.memory.read(n1 << 8 | n2)
			self.pc+=3; cycles=4

		elif opcode == 0b11101010:
			n1 = self.memory.read(self.pc+1)
			n2 = self.memory.read(self.pc+2)
			self.memory.write((n1 << 8) | n2, self.r["a"])
			self.pc+=3; cycles=4

		elif opcode == 0b00101010:
			t = (self.r["h"] << 8) | self.r["l"]
			self.r["a"] = self.memory.read(t)
			t += 1
			self.r["h"]=t>>8
			self.r["l"]=t&0x00FF
			self.pc+=1; cycles=2

		elif opcode == 0b00111010:
			t = (self.r["h"] << 8) | self.r["l"]
			self.r["a"] = self.memory.read(t)
			t -= 1
			self.r["h"]=t>>8
			self.r["l"]=t&0x00FF
			self.pc+=1; cycles=2

		elif opcode == 0b00000010:
			self.memory.write((self.r["b"]<<8)|self.r["c"], self.r["a"])
			self.pc+=1; cycles=2

		elif opcode == 0b00010010:
			self.memory.write((self.r["d"]<<8)|self.r["e"], self.r["a"])
			self.pc+=1; cycles=2

		elif opcode == 0b00100010:
			t = (self.r["h"] << 8) | self.r["l"]
			self.memory.write(t, self.r["a"])
			t+=1
			self.r["h"]=t>>8
			self.r["l"]=t&0x00FF
			self.pc+=1; cycles=2

		elif opcode == 0b00110010:
			t = (self.r["h"] << 8) | self.r["l"]
			self.memory.write(t, self.r["a"])
			t-=1
			self.r["h"]=t>>8
			self.r["l"]=t&0x00FF
			self.pc+=1; cycles=2

		elif opcode & 0b11001111 == 0b00000001:
			n1 = self.memory.read(self.pc+1)
			n2 = self.memory.read(self.pc+2)
			dd = CPU.pairMap[(opcode&0b00110000) >> 4]

			self.r[dd[0]] = n1
			self.r[dd[1]] = n2

			self.pc+=3; cycles=3

		elif opcode == 0b11111001:
			self.r["sp"] = (self.r["h"] << 8) | self.r["l"]
			self.pc+=1; cycles=2

		elif opcode & 0b11001111 == 0b11000101:
			dd = CPU.pairMap[(opcode&0b00110000) >> 4]
			self.memory.write(self.r["sp"]-1, self.r[dd[0]])
			self.memory.write(self.r["sp"]-2, self.r[dd[1]])
			self.r["sp"]-=2
			self.pc+=1; cycles=4

		elif opcode & 0b11001111 == 0b110000001:
			dd = CPU.pairMap[(opcode&0b00110000) >> 4]
			self.r[dd[1]] = self.r["sp"]-1
			self.r[dd[0]] = self.r["sp"]-2
			self.r["ps"]+=2
			self.pc+=1; cycles=3

		elif opcode == 0b11111000:
			e = self.memory.read(self.pc+1) #2's complement
			temp = self.r["sp"]
			if e & 0x80:
				e = e - 0x100

			val = self.r["sp"] + e

			self.r["h"] = val >> 8
			self.r["l"] = val & 0xFF

			""" Code below is found here: http://stackoverflow.com/questions/5159603/gbz80-how-does-ld-hl-spe-affect-h-and-c-flags
				It is an answer suggested by Fascia. """

			if e >= 0:
				setflag(2, ((self.r["sp"] & 0xF) + (e & 0xF)) > 0xF)
				setflag(3, ((self.r["sp"] & 0xFF) + e) > 0xFF)
			else:
				setflag(2, (temp & 0xF) <= (self.r["sp"] & 0xF))
				setflag(3, (temp & 0xFF) <= (self.r["sp"] & 0xFF))

			cycles=3; self.pc+=2

		elif opcode == 0b00001000:
			self.memory.write(self.r["sp"]&0xFF, self.pc+1)
			self.memory.write(self.r["sp"]>>8, self.pc+2)
			cycles=5; self.pc+=3

		elif opcode & 0b11111000 == 0b10000000:
			self.r["a"] = add(self.r["a"], CPU.byteRegMap[opcode&0b00000111])
			cycles=1; self.pc+=1

		elif opcode == 0b11000110:
			self.r["a"] = add(self.r["a"], self.memory.read(self.pc+1))
			cycles=2; self.pc+=2

		elif opcode == 0b10000110:
			self.r["a"] = add(self.r["a"], read((self.r["h"]<<8) | self.r["l"]))
			cycles=2; self.pc+=1

		elif opcode & 0b11000111 == 0b00000100:
			old = self.r[CPU.byteRegMap[(opcode&0b00111000)>>3]]
			result = old + 1
			setflag(0, result == 0)
			setflag(1, 0)
			setflag(2, ((old&0xF) + 1) > 0xF)
			
			self.r[CPU.byteRegMap[(opcode&0b00111000)>>3]]=result
			cycles=1; self.pc+=1

		elif opcode == 0b00110100:
			old = read((self.r["h"]<<8)|self.r["l"])
			result = old + 1
			setflag(0, result == 0)
			setflag(1, 0)
			setflag(2, ((old&0xF) + 1) > 0xF)

			self.memory.write((self.r["h"]<<8)|self.r["l"], result)
			cycles=3; self.pc+=1

		elif opcode & 0b11000111 == 0b00000101:
			old = self.r[CPU.byteRegMap[(opcode&0b00111000)>>3]]
			result = old - 1
			setflag(0, result == 0)
			setflag(1, 1)
			setflag(2, ((old&0xF) - 1) > 0xF)

			self.r[CPU.byteRegMap[(opcode&0b00111000)>>3]]=result
			cycles=1; self.pc+=1

		elif opcode == 0b00110101:
			old = read((self.r["h"]<<8)|self.r["l"])
			result = old - 1
			setflag(0, result == 0)
			setflag(1, 1)
			setflag(2, ((old&0xF) - 1) > 0xF)

			self.memory.write((self.r["h"]<<8)|self.r["l"], result)
			cycles=3; self.pc+=1

		# 16 Bit Artimetic Operations

		elif opcode & 0b11001111 == 0b00001001:
			register = CPU.pairMap[(opcode&0b00110000)>>4]
			value = (registeself.r[0] << 8) | registeself.r[1]
			reg = self.r["h"] << 8 | self.r["l"]
			
			setflag(1, 0)
			setflag(2, (value&0xF) + (reg*0xF) > 0xF)
			setflag(3, value + reg > 0xFF)

			reg += value
			cycles=2; self.pc+=1

		elif opcode == 0b11101000:
			e = self.memory.read(self.pc+1) #2's complement
			temp = self.r["sp"]
			if e & 0x80:
				e = e - 0x100

			self.r["sp"]+=e

			""" Code below is found here: http://stackoverflow.com/questions/5159603/gbz80-how-does-ld-hl-spe-affect-h-and-c-flags
				It is an answer suggested by Fascia. """

			if e >= 0:
				setflag(2, ((self.r["sp"] & 0xF) + (e & 0xF)) > 0xF)
				setflag(3, ((self.r["sp"] & 0xFF) + e) > 0xFF)
			else:
				setflag(2, (temp & 0xF) <= (self.r["sp"] & 0xF))
				setflag(3, (temp & 0xFF) <= (self.r["sp"] & 0xFF))

			cycles=4; self.pc+=2

		elif opcode & 0b11001111 == 0b00000011:
			register = CPU.pairMap[(opcode&0b00110000)>>4]
			value = ((self.r[registeself.r[0]] << 8)  | self.r[registeself.r[1]]) + 1

			self.r[registeself.r[0]] = value >> 8
			self.r[registeself.r[1]] = value & 0xFF

			cycles=2; self.pc+=1

		elif opcode & 0b11001111 == 0b00001011:
			register = CPU.pairMap[(opcode&0b00110000)>>4]
			value = ((self.r[registeself.r[0]] << 8)  | self.r[registeself.r[1]]) - 1

			self.r[registeself.r[0]] = value >> 8
			self.r[registeself.r[1]] = value & 0xFF
			cycles=2; self.pc+=1

		# Rotate Shift Operations
		elif opcode == 0b00000111:
			setflag(3, self.r["a"][0])

			self.r["a"] = self.r["a"] << 1
			setflag(0, self.r["a"] == 0)

			cycles=1; self.pc+=1

		elif opcode == 0b00010111:
			self.r["a"] = self.r["a"] << 1

			setflag(3, self.r["a"][0])
			setflag(0, self.r["a"] == 0)

			cycles=1; self.pc+=1

		elif opcode == 0b00001111:
			setflag(3, self.r["a"][7])
			
			self.r["a"] = self.r["a"] >> 1
			setflag(0, self.r["a"] == 0)

			cycles=1; self.pc+=1

		elif opcode == 0b00011111:
			self.r["a"] = self.r["a"] >> 1

			setflag(3, self.r["a"][7])
			setflag(0, self.r["a"] == 0)

			cycles=1; self.pc+=1

		# Bit Operations
		elif opcode == 0b11001011:
			# Multiple commands for this opcode
			nextop = self.memory.read(self.pc+1)
			cycles = 0 

			if nextop & 0b11000000 == 0b01000000:
				bit = (nextop&0b00111000) >> 3
				if nextop & 0b00000111 == 0b110:
					setflag(0, (read((self.r["h"]<<8)|self.r["l"])&(0b1<<bit)))
					cycles = 3
				else:
					setflag(0, self.r[CPU.byteRegMap[nextop&0b00000111]]&(0b1<<bit))
					cycles = 2

				setflag(1, 0)
				setflag(2, 1)

			elif nextop & 0b11000000 == 0b11000000:
				bit = (nextop&0b00111000) >> 3
				if nextop & 0b00000111 == 0b110:
					result = ((self.r["h"]<<8) | self.r["l"]) | (0b1<<bit)

					self.r["h"] = result >> 8
					self.r["l"] = result & 0x00FF

					cycles = 4

				else:
					self.r[CPU.byteRegMap[nextop&0b00000111]] |= 0b1 << bit

					cycles = 2

			elif nextop & 0b11000000 == 0b10000000:
				bit = (nextop&0b00111000) >> 3
				if nextop & 0b00000111 == 0b110:
					result = ((self.r["h"]<<8) | self.r["l"]) ^ (0b1 << bit)

					self.r["h"] = result >> 8
					self.r["l"] = result & 0x00FF

					cycles = 4
				else:
					self.r[CPU.byteRegMap[nextop&0b00000111]] ^= 0b1 << bit
					cycles = 2

				self.pc+=2

		# Function Jump Operations
		elif opcode == 0b11000011:
			n1 = self.memory.read(self.pc+1)
			n2 = self.memory.read(self.pc+2)

			self.pc = (n1 << 8) | n2

			cycles = 4

		elif opcode & 0b11100111 == 0b11000010:
			flag = CPU.flagMap[(opcode&0b00011000)>>3]

			if getflag(flag[0]) == flag[1]:
				n1 = self.memory.read(self.pc+1)
				n2 = self.memory.read(self.pc+2)
				self.pc = (n1 << 8) | n2
				cycles = 4
			else:
				cycles = 3
				self.pc+=3

		elif opcode == 0b00011000:
			e = self.memory.read(self.pc+1)
			if e & 0x80:
				e = e - 0x100

			self.pc += e

			cycles=3

		elif opcode & 0b11100111 == 0b00100000:
			flag = CPU.flagMap[(opcode&0b00011000)>>3]

			if getflag(flag[0]) == flag[1]:
				e = self.memory.read(self.pc+1)
				if e & 0x80:
					e = e - 0x100

				self.pc += e
				cycles = 4
			else:
				self.pc+=2
				cycles = 3

		elif opcode == 0b11101001:
			self.pc = (self.r["h"]<<8)|self.r["l"]
			cycles=1

		# Call/Return Instructions	
		elif opcode == 0b11000011:
			self.memory.write(self.r["sp"]-1, self.pc>>8)
			self.memory.write(self.r["sp"]-2, self.pc&0xFF)

			n1 = self.memory.read(self.pc+1)
			n2 = self.memory.read(self.pc+2)

			self.pc = (n1 << 8) | n2

			self.r["sp"] -= 2

			cycles=6

		elif opcode & 0b11100111 == 0b11000100:
			flag = CPU.flagMap[(opcode&0b00011000)>>3]

			if getflag(flag[0]) == flag[1]:
				self.memory.write(self.r["sp"]-1, self.pc>>8)
				self.memory.write(self.r["sp"]-2, self.pc&0xFF)

				n1 = self.memory.read(self.pc+1)
				n2 = self.memory.read(self.pc+2)

				self.pc = (n1 << 8) | n2

				self.r["sp"] -= 2

				cycles=6
			else:
				cycles=3
				self.pc+=1

		elif opcode == 0b11001001 or opcode == 0b11011001:
			sp1 = self.memory.read(self.r["sp"])
			sp2 = self.memory.read(self.r["sp"]+1)

			self.r["ime"] = 0
			if opcode == 0b11011001:
				self.r["ime"] = 1

			self.pc = (sp2 << 8) | sp1
			self.r["sp"] += 2
			cycles = 4
			
		elif opcode & 0b11100111 == 0b11000000:
			flag = CPU.flagMap[(opcode&0b00011000)>>3]
			if getflag(flag[0]) == flag[1]:
				sp1 = self.memory.read(self.r["sp"])
				sp2 = self.memory.read(self.r["sp"]+1)

				self.pc = (sp2 << 8) | sp1
				self.r["sp"] += 2
				cycles = 5
			else:
				cycles = 2

		elif opcode & 0b11000111 == 0b11000111:
			value = CPU.tMap[(opcode&0b00111000)>>3]

			self.pc = value

			cycles = 4

		# General Purpose Instructions
		elif opcode == 0b00100111:
			# Don't care at this point
			cycles = 1; self.pc+=1

		elif opcode == 0b00101111:
			self.r["a"] ^= 0xFF
			cycles = 1; self.pc+=1 

		elif opcode == 0b00000000:
			cycles=1; self.pc+=1

		elif opcode == 0b00111111:
			setflag(1, 1)
			setflag(2, 1)
			setflag(3, getflag(3)^1)

			cycles=1; self.pc+=1

		elif opcode == 0b00110111:
			setflag(1, 1)
			setflag(2, 1)
			setflag(3, 1)

			cycles=1; self.pc+=1

		elif opcode == 0b11110011:
			self.r["ime"] = 0
			cycles = 1; self.pc+=1

		elif opcode == 0b11111011:
			self.r["ime"] = 1
			cycles = 1; self.pc+=1

		elif opcode == 0b01110110:
			cycles=1; self.pc+=1

		elif opcode == 0b00010000:
			exit()

		else:
			print("Executed Illegal Opcode: ")
			print(hex(opcode))

			print("Terminating...")
			exit()

		print("Opcode Executed:")
		print(bin(opcode))


		self.clock += cycles

