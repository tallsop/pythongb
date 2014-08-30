from memory import *

running = True

clock = 4
cycles = 0

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

# All values are set to their initial values upon the systems startup
r = {"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"h":0,"l":0,
	"sp":0xFFFE}

pc = 0x100

# Bytes in opcode which refer to register
# Do not write over this! :D
byteRegMap = { 0b111:"a", 0b000:"b", 0b001:"c", 0b010:"d", 0b011:"e", 0b100:"h", 0b101:"l" }

pairMap = { 0b00:"bc", 0b01:"de", 0b10:"hl", 0b11:"sp" }


""" Helper Functions """
def setflag(n,val):
	mask = "0000"
	mask[n] = str(val)

	r["f"] = r["f"] | (int(mask) << 4)
	return r["f"]

def getflag(n):
	return r["f"][n]

def add(a,b):
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


while running:
	opcode = read(pc)

	""" 
	Here is where opcodes are executed in the order of the Game Boy manual with exceptions where
	the masking of an opcode causes the wrong one to be executed, in these cases, the exact opcode
	copy is placed above the one which is causing problems.
	"""

	""" TODO: Correct the CPU Clocks """

	if opcode & 0b11000000 == 0b01000000:
		t = opcode & 0b00111111
		r[byteRegMap[t>>3]] = r[byteRegMap[t&0b00000111]]
		pc+=1; cycles=1

	elif opcode & 0b11000111 == 0b00000110:
		t = read(pc+1)
		r[byteRegMap[(opcode&0b00111000)>>3]] = t
		pc+=2; cycles=2

	elif opcode & 0b11000111 == 0b01000110:
		r[byteRegMap[(opcode&0b00111000)>>3]] = read((r["h"] << 8) | r["l"])
		pc+=1; cycles=2

	elif opcode & 0b11111000 == 0b01110000:
		t = h[byteRegMap[opcode&0b00000111]]
		write((r["h"] << 8) | r["l"], t)
		pc+=1; cycles=2

	elif opcode == 0b00110110:
		n = read(pc+1)
		write((r["h"] << 8) | r["l"], n)
		pc+=2; cycles=3

	elif opcode == 0b00001010:
		r["a"] = read((r["b"] << 8) | r["c"])
		pc+=1; cycles=2

	elif opcode == 0b00011010:
		r["a"] = read((r["d"] << 8) | r["e"])
		pc+=1; cycles=2

	elif opcode == 0b11110010:
		r["a"] = read(0xFF00 + r["c"])
		pc+=1; cycles=2

	elif opcode == 0b11100010:
		write(0xFF00 + r["c"], r["a"])
		pc+=1; cycles=2

	elif opcode == 0b11110000:
		n = read(pc+1)
		r["a"] = read(n)
		pc+=2; cycles=3

	elif opcode == 0b11100000:
		n = read(pc+1)
		write(n, r["a"])
		pc+=2; cycles=3

	elif opcode == 0b11111010:
		n1 = read(pc+1)
		n2 = read(pc+2)
		r["a"]= read(n1 << 8 | n2)
		pc+=3; cycles=4

	elif opcode == 0b11101010:
		n1 = read(pc+1)
		n2 = read(pc+2)
		write((n1 << 8) | n2, r["a"])
		pc+=3; cycles=4

	elif opcode == 0b00101010:
		t = (r["h"] << 8) | r["l"]
		r["a"] = read(t)
		t += 1
		r["h"]=t>>8
		r["l"]=t&0x00FF
		pc+=1; cycles=2

	elif opcode == 0b00111010:
		t = (r["h"] << 8) | r["l"]
		r["a"] = read(t)
		t -= 1
		r["h"]=t>>8
		r["l"]=t&0x00FF
		pc+=1; cycles=2

	elif opcode == 0b00000010:
		write((r["b"]<<8)|r["c"], r["a"])
		pc+=1; cycles=2

	elif opcode == 0b00010010:
		write((r["d"]<<8)|r["e"], r["a"])
		pc+=1; cycles=2

	elif opcode == 0b00100010:
		t = (r["h"] << 8) | r["l"]
		write(t, r["a"])
		t+=1
		r["h"]=t>>8
		r["l"]=t&0x00FF
		pc+=1; cycles=2

	elif opcode == 0b00110010:
		t = (r["h"] << 8) | r["l"]
		write(t, r["a"])
		t-=1
		r["h"]=t>>8
		r["l"]=t&0x00FF
		pc+=1; cycles=2

	elif opcode & 0b11001111 == 0b00000001:
		n1 = read(pc+1)
		n2 = read(pc+2)
		dd = pairMap[(opcode&0b00110000) >> 4]

		r[dd[0]] = n1
		r[dd[1]] = n2

		pc+=3; cycles=3

	elif opcode == 0b11111001:
		r["sp"] = (r["h"] << 8) | r["l"]
		pc+=1; cycles=2

	elif opcode & 0b11001111 == 0b11000101:
		dd = pairMap[(opcode&0b00110000) >> 4]
		write(r["sp"]-1, r[dd[0]])
		write(r["sp"]-2, r[dd[1]])
		r["sp"]-=2
		pc+=1; cycles=4

	elif opcode & 0b11001111 == 0b110000001:
		dd = pairMap[(opcode&0b00110000) >> 4]
		r[dd[1]] = r["sp"]-1
		r[dd[0]] = r["sp"]-2
		r["ps"]+=2
		pc+=1; cycles=3

	elif opcode == 0b11111000:
		e = read(pc+1) #2's complement
		temp = r["sp"]
		if e & 0x80:
			e = e - 0x100

		val = r["sp"] + e

		r["h"] = val >> 8
		r["l"] = val & 0xFF

		""" Code below is found here: http://stackoverflow.com/questions/5159603/gbz80-how-does-ld-hl-spe-affect-h-and-c-flags
			It is an answer suggested by Fascia. """

		if e >= 0:
			setflag(2, ((r["sp"] & 0xF) + (e & 0xF)) > 0xF)
			setflag(3, ((r["sp"] & 0xFF) + e) > 0xFF)
		else:
			setflag(2, (temp & 0xF) <= (r["sp"] & 0xF))
			setflag(3, (temp & 0xFF) <= (r["sp"] & 0xFF))

		cycles=3; pc+=2

	elif opcode == 0b00001000:
		write(r["sp"]&0xFF, pc+1)
		write(r["sp"]>>8, pc+2)
		cycles=5; pc+=3

	elif opcode & 0b11111000 == 0b10000000:
		r["a"] = add(r["a"], byteRegMap[opcode&0b00000111])
		cycles=1; pc+=1

	elif opcode == 0b11000110:
		r["a"] = add(r["a"], read(pc+1))
		cycles=2; pc+=2

	elif opcode == 0b10000110:
		r["a"] = add(r["a"], read((r["h"]<<8) | r["l"]))
		cycles=2; pc+=1

	elif opcode & 0b11000111 == 0b00000100:
		old = r[byteRegMap[(opcode&0b00111000)>>3]]
		result = old + 1
		setflag(0, result == 0)
		setflag(1, 0)
		setflag(2, ((old&0xF) + 1) > 0xF)
		
		r[byteRegMap[(opcode&0b00111000)>>3]]=result
		cycles=1; pc+=1

	elif opcode == 0b00110100:
		old = read((r["h"]<<8)|r["l"]))
		result = old + 1
		setflag(0, result == 0)
		setflag(1, 0)
		setflag(2, ((old&0xF) + 1) > 0xF)

		write((r["h"]<<8)|r["l"], result)
		cycles=3; pc+=1

	elif opcode & 0b11000111 == 0b00000101:
		old = r[byteRegMap[(opcode&0b00111000)>>3]]
		result = old - 1
		setflag(0, result == 0)
		setflag(1, 1)
		setflag(2, ((old&0xF) - 1) > 0xF)

		r[byteRegMap[(opcode&0b00111000)>>3]]=result
		cycles=1; pc+=1

	elif opcode == 0b00110101:
		old = read((r["h"]<<8)|r["l"]))
		result = old - 1
		setflag(0, result == 0)
		setflag(1, 1)
		setflag(2, ((old&0xF) - 1) > 0xF)

		write((r["h"]<<8)|r["l"], result)
		cycles=3; pc+=1

	# 16 Bit Artimetic Operations

	elif opcode & 0b11001111 == 0b00001001:
		register = pairMap[(opcode&0b00110000)>>4]
		value = (register[0] << 8) | register[1]
		reg = r["h"] << 8 | r["l"]
		
		setflag(1, 0)
		setflag(2, (value&0xF) + (reg*0xF) > 0xF)
		setflag(3, value + reg > 0xFF)

		reg += value
		cycles=2; pc+=1

	elif opcode == 0b11101000:
		e = read(pc+1) #2's complement
		temp = r["sp"]
		if e & 0x80:
			e = e - 0x100

		r["sp"]+=e

		""" Code below is found here: http://stackoverflow.com/questions/5159603/gbz80-how-does-ld-hl-spe-affect-h-and-c-flags
			It is an answer suggested by Fascia. """

		if e >= 0:
			setflag(2, ((r["sp"] & 0xF) + (e & 0xF)) > 0xF)
			setflag(3, ((r["sp"] & 0xFF) + e) > 0xFF)
		else:
			setflag(2, (temp & 0xF) <= (r["sp"] & 0xF))
			setflag(3, (temp & 0xFF) <= (r["sp"] & 0xFF))

		cycles=4; pc+=2

	elif opcode & 0b11001111 == 0b00000011:
		register = pairMap[(opcode&0b00110000)>>4]
		value = ((r[register[0]] << 8)  | r[register[1]]) + 1

		r[register[0]] = value >> 8
		r[register[1]] = value & 0xFF

		cycles=2; pc+=1

	elif opcode & 0b11001111 == 0b00001011:
		register = pairMap[(opcode&0b00110000)>>4]
		value = ((r[register[0]] << 8)  | r[register[1]]) - 1

		r[register[0]] = value >> 8
		r[register[1]] = value & 0xFF
		cycles=2; pc+=1

	# Rotate Shift Operations
	elif opcode == 0b00000111:
		setflag(3, r["a"][0])

		r["a"] = r["a"] << 1
		setflag(0, r["a"] == 0)

		cycles=1; pc+=1

	elif opcode == 0b00010111:
		r["a"] = r["a"] << 1

		setflag(3, r["a"][0])
		setflag(0, r["a"] == 0)

		cycles=1; pc+=1

	elif opcode == 0b00001111:
		setflag(3, r["a"][7])
		
		r["a"] = r["a"] >> 1
		setflag(0, r["a"] == 0)

		cycles=1; pc+=1

	elif opcode == 0b00011111:
		r["a"] = r["a"] >> 1

		setflag(3, r["a"][7])
		setflag(0, r["a"] == 0)

		cycles=1; pc+=1

	# Bit Operations
	elif opcode == 0b11001011:
		# Multiple commands for this opcode
		nextop = read(pc+1)
		cycles = 0 

		if nextop & 0b11000000 == 0b01000000:
			bit = (nextop&0b00111000) >> 3
			if nextop & 0b00000111 == 0b110:
				setflag(0, (read((r["h"]<<8)|r["l"])&(0b1<<bit)))
				cycles = 3
			else:
				setflag(0, r[byteRegMap[nextop&0b00000111]]&(0b1<<bit))
				cycles = 2

			setflag(1, 0)
			setflag(2, 1)

		elif nextop & 0b11000000 == 0b11000000:
			bit = (nextop&0b00111000) >> 3
			if nextop & 0b00000111 == 0b110:
				result = ((r["h"]<<8) | r["l"]) | (0b1<<bit)

				r["h"] = result >> 8
				r["l"] = result & 0x00FF

				cycles = 4

			else:
				r[byteRegMap[nextop&0b00000111]] |= 0b1 << bit

				cycles = 2

		elif nextop & 0b11000000 == 0b10000000:
			bit = (nextop&0b00111000) >> 3
			if nextop & 0b00000111 == 0b110:
				result = ((r["h"]<<8) | r["l"]) ^ (0b1 << bit)

				r["h"] = result >> 8
				r["l"] = result & 0x00FF

				cycles = 4
			else:
				r[byteRegMap[nextop&0b00000111]] ^= 0b1 << bit#
				cycles = 2

		pc+=2

	# Function Jump Operations
	elif opcode == 0b11000011:
		n1 = read(pc+1)
		n2 = read(pc+2)

		pc = (n1 << 8) | n2

		cycles = 4; pc+=3


	""" When interrupts need to be checked """
	if clock <= 0:
		clock += 4
