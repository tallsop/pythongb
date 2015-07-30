from datetime import datetime

"""
Memory Map
------------
"""


class MemoryController(object):
    bios = [0x31, 0xfe, 0xff, 0xaf, 0x21, 0xff, 0x9f, 0x32, 0xcb,
            0x7c, 0x20, 0xfb, 0x21, 0x26, 0xff, 0x0e, 0x11, 0x3e,
            0x80, 0x32, 0xe2, 0x0c, 0x3e, 0xf3, 0xe2, 0x32, 0x3e,
            0x77, 0x77, 0x3e, 0xfc, 0xe0, 0x47, 0x11, 0x04, 0x01,
            0x21, 0x10, 0x80, 0x1a, 0xcd, 0x95, 0x00, 0xcd, 0x96,
            0x00, 0x13, 0x7b, 0xfe, 0x34, 0x20, 0xf3, 0x11, 0xd8,
            0x00, 0x06, 0x08, 0x1a, 0x13, 0x22, 0x23, 0x05, 0x20,
            0xf9, 0x3e, 0x19, 0xea, 0x10, 0x99, 0x21, 0x2f, 0x99,
            0x0e, 0x0c, 0x3d, 0x28, 0x08, 0x32, 0x0d, 0x20, 0xf9,
            0x2e, 0x0f, 0x18, 0xf3, 0x67, 0x3e, 0x64, 0x57, 0xe0,
            0x42, 0x3e, 0x91, 0xe0, 0x40, 0x04, 0x1e, 0x02, 0x0e,
            0x0c, 0xf0, 0x44, 0xfe, 0x90, 0x20, 0xfa, 0x0d, 0x20,
            0xf7, 0x1d, 0x20, 0xf2, 0x0e, 0x13, 0x24, 0x7c, 0x1e,
            0x83, 0xfe, 0x62, 0x28, 0x06, 0x1e, 0xc1, 0xfe, 0x64,
            0x20, 0x06, 0x7b, 0xe2, 0x0c, 0x3e, 0x87, 0xe2, 0xf0,
            0x42, 0x90, 0xe0, 0x42, 0x15, 0x20, 0xd2, 0x05, 0x20,
            0x4f, 0x16, 0x20, 0x18, 0xcb, 0x4f, 0x06, 0x04, 0xc5,
            0xcb, 0x11, 0x17, 0xc1, 0xcb, 0x11, 0x17, 0x05, 0x20,
            0xf5, 0x22, 0x23, 0x22, 0x23, 0xc9, 0xce, 0xed, 0x66,
            0x66, 0xcc, 0x0d, 0x00, 0x0b, 0x03, 0x73, 0x00, 0x83,
            0x00, 0x0c, 0x00, 0x0d, 0x00, 0x08, 0x11, 0x1f, 0x88,
            0x89, 0x00, 0x0e, 0xdc, 0xcc, 0x6e, 0xe6, 0xdd, 0xdd,
            0xd9, 0x99, 0xbb, 0xbb, 0x67, 0x63, 0x6e, 0x0e, 0xec,
            0xcc, 0xdd, 0xdc, 0x99, 0x9f, 0xbb, 0xb9, 0x33, 0x3e,
            0x3c, 0x42, 0xb9, 0xa5, 0xb9, 0xa5, 0x42, 0x3c, 0x21,
            0x04, 0x01, 0x11, 0xa8, 0x00, 0x1a, 0x13, 0xbe, 0x20,
            0xfe, 0x23, 0x7d, 0xfe, 0x34, 0x20, 0xf5, 0x06, 0x19,
            0x78, 0x86, 0x23, 0x05, 0x20, 0xfb, 0x86, 0x20, 0xfe,
            0x3e, 0x01, 0xe0, 0x50]

    def __init__(self, debug):
        self.debug = debug
        self.bios_use = True

        # ROM Only - 0, MBC1 - 1, MBC2 - 2, MBC3 - 3, MB5 - 5
        self.banking_type = 0

        # Select the bank in the ROM
        self.curr_bank = 1

        # 0 - 16Mbit ROM 8KByte RAM and 1 - Select 4Mbit ROM 32KByte RAM
        self.memory_model = 0

        self.disable_eram = False
        self.eram_bank = 0

        self.disable_rtc = False
        self.map_rtc = False

        self.latch_rtc = 0

        # Time Registers
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.days = 0
        self.flags = 0

        self.rom = bytearray(0x8000)  # 0x0000 - 0x8000 (Override with game rom)
        self.vram = bytearray(0xA000 - 0x8000)  # 0x8000 - 0xA000
        self.eram = bytearray((0xC000 - 0xA000) + 0x2000 * 0x0F)  # 0xA000 - 0xC000 (Extra if the eram is banked)
        self.wram = bytearray(0xE000 - 0xC000)  # 0xC000 - 0xE000 Echoed to: 0xE000 - 0xFE00
        self.oam = bytearray(0xFEA0 - 0xFE00)  # 0xFE00 - 0xFEA0
        # 0xFEA0 - 0xFF00 Unused
        self.io = bytearray(0xFF4C - 0xFF00)  # 0xFF00- 0xFF4C
        # 0xFF4C - 0xFF80 is empty
        self.ram = bytearray(0xFFFF - 0xFF80)  # 0xFF80 - 0xFFFF

        # GPU Reference (Empty until attached)
        self.gpu = None

    def read0(self, loc):
        # At the start of the emulation the bios is in use
        if loc <= 0x100:
            # At the start of the emulation the bios is in use
            if self.bios_use:
                if loc == 0x100:
                    self.bios_use = False
                    return self.rom[loc]
                
                return MemoryController.bios[loc]

            return self.rom[loc]
        if loc < 0x1000:
            return self.rom[loc]
        elif loc < 0x4000:
            return self.rom[loc]
        elif loc < 0x8000:
            return self.rom[loc]
        elif loc < 0xA000:
            return self.vram[loc - 0x8000]
        elif loc < 0xC000:
            return self.eram[loc - 0xA000]
        elif loc < 0xE000:
            return self.wram[loc - 0xC000]
        elif loc < 0xFE00:
            return self.wram[loc - 0xE000]
        elif loc < 0xFEA0:
            return self.oam[loc - 0xFE00]
        elif loc < 0xFF00:
            return 0x0
        elif loc < 0xFF4C:
            return self.io[loc - 0xFF00]
        elif loc < 0xFF80:
            return 0x0
        elif loc < 0xFFFF:
            return self.ram[loc - 0xFF80]

        return 0

    # MBC1 Banking
    def read1(self, loc):
        if loc < 0x255:
            # At the start of the emulation the bios is in use
            if self.bios_use and loc < len(MemoryController.bios):
                if (loc - 0x100) >= len(MemoryController.bios) - 1:
                    self.bios_use = False

                return MemoryController.bios[loc - 0x100]

            return self.rom[loc]
        elif loc < 0x4000:
            return self.rom[loc]
        elif loc < 0x8000:
            return self.rom[loc - 0x4000 + (0x4000 * self.currBank)]
        elif loc < 0xA000:
            return self.vram[loc - 0x8000]
        elif loc < 0xC000:
            return self.eram[loc - 0xA000 + (0x2000 * self.eram_bank)]
        elif loc < 0xE000:
            return self.wram[loc - 0xC000]
        elif loc < 0xFE00:
            return self.wram[loc - 0xE000]
        elif loc < 0xFEA0:
            return self.oam[loc - 0xFE00]
        elif loc < 0xFF4C:
            return self.io[loc - 0xFF00]
        elif loc < 0xFFFF:
            return self.ram[loc - 0xFF80]

        return 0

    # MBC2 Banking
    def read2(self, loc):
        # At the start of the emulation the bios is in use
        if loc < 0x1000:
            # At the start of the emulation the bios is in use
            if self.bios_use:
                if (loc - 0x100) >= len(MemoryController.bios) - 1:
                    self.bios_use = False

                return MemoryController.bios[loc - 0x100]

            return self.rom[loc]
        elif loc < 0x4000:
            return self.rom[loc]
        elif loc < 0x8000:
            return self.rom[loc - 0x4000 + (0x4000 * self.currBank)]
        elif loc < 0xA000:
            return self.vram[loc - 0x8000]
        elif loc < 0xC000:
            return self.eram[loc - 0xA000] & 0x00FF  # Only lower 4 bits are used
        elif loc < 0xE000:
            return self.wram[loc - 0xC000]
        elif loc < 0xFE00:
            return self.wram[loc - 0xE000]
        elif loc < 0xFEA0:
            return self.oam[loc - 0xFE00]
        elif loc < 0xFF4C:
            return self.io[loc - 0xFF00]
        elif loc < 0xFFFF:
            return self.ram[loc - 0xFF80]

        return 0

    # MBC3 Banking
    def read3(self, loc):
        # At the start of the emulation the bios is in use
        if loc < 0x1000:
            # At the start of the emulation the bios is in use
            if self.bios_use and loc < len(MemoryController.bios):
                if (loc - 0x100) >= len(MemoryController.bios) - 1:
                    self.bios_use = False

                return MemoryController.bios[loc - 0x100]

            return self.rom[loc]
        elif loc < 0x4000:
            return self.rom[loc]
        elif loc < 0x8000:
            return self.rom[loc - 0x4000 + (0x4000 * self.currBank)]
        elif loc < 0xA000:
            return self.vram[loc - 0x8000]
        elif loc < 0xC000:
            if not self.disable_eram:
                if not self.map_rtc:
                    return self.eram[loc - 0xA000 + (0x2000 * self.eram_bank)]
                else:
                    # TODO: Implement the register mappings
                    pass
        elif loc < 0xE000:
            return self.wram[loc - 0xC000]
        elif loc < 0xFE00:
            return self.wram[loc - 0xE000]
        elif loc < 0xFEA0:
            return self.oam[loc - 0xFE00]
        elif loc < 0xFF4C:
            return self.io[loc - 0xFF00]
        elif loc < 0xFFFF:
            return self.ram[loc - 0xFF80]

        return 0

    # MBC5 Banking
    def read5(self, loc):
        # At the start of the emulation the bios is in use
        if loc < 0x1000:
            # At the start of the emulation the bios is in use
            if self.bios_use and loc < len(MemoryController.bios):
                if (loc - 0x100) >= len(MemoryController.bios) - 1:
                    self.bios_use = False

                return MemoryController.bios[loc - 0x100]

            return self.rom[loc]
        elif loc < 0x4000:
            return self.rom[loc]
        elif loc < 0x8000:
            return self.rom[loc - 0x4000 + (0x4000 * self.currBank)]
        elif loc < 0xA000:
            return self.vram[loc - 0x8000]
        elif loc < 0xC000:
            return self.eram[loc - 0xA000] & 0x00FF  # Only lower 4 bits are used
        elif loc < 0xE000:
            return self.wram[loc - 0xC000]
        elif loc < 0xFE00:
            return self.wram[loc - 0xE000]
        elif loc < 0xFEA0:
            return self.oam[loc - 0xFE00]
        elif loc < 0xFF4C:
            return self.io[loc - 0xFF00]
        elif loc < 0xFFFF:
            return self.ram[loc - 0xFF80]

        return 0

    def read(self, loc):
        banking_functions = {
            0: self.read0,
            1: self.read1,
            2: self.read2,
            3: self.read3,
            5: self.read5
        }

        return banking_functions[self.banking_type](loc)

    # ROM Only Banking
    def write0(self, loc, data):
        # This is for selecting the appropriate bank
        if loc < 0x8000:
            self.rom[loc] = data
        elif loc < 0x9800:
            # Update the tile data
            self.gpu.update_tiles(loc)
            return self.vram[loc - 0x8000]
        elif loc < 0xA000:
            self.vram[loc - 0x8000] = data
        elif loc < 0xC000:
            self.eram[loc - 0xA000 + (0x2000 * self.eram_bank)] = data
        elif loc < 0xE000:
            self.wram[loc - 0xC000] = data
        elif loc < 0xFE00:
            self.wram[loc - 0xE000] = data
        elif loc < 0xFEA0:
            self.oam[loc - 0xFE00] = data
        elif loc < 0xFF4C:
            self.io[loc - 0xFF00] = data
        elif loc < 0xFFFF:
            self.ram[loc - 0xFF80] = data

    # MBC1 Banking
    def write1(self, loc, data):
        if 0x0000 <= loc < 0x2000:
            if loc & 0x0A:
                self.disable_eram = False
            else:
                self.disable_eram = True

        elif 0x2000 <= loc < 0x4000:
            # Take 0bXXXBBBBB where B = bank select bits
            # This will select a bank for 0x4000 - 0x7FFF to map to in ROM
            bank = loc & 0b00011111

            # Now map the bank on info we know
            # 0 and 1 map to bank 1

            # 0x20, 0x40 and 0x60 are unused, created 125 banks
            if bank == 0:
                self.currBank = 1
            elif bank == 0x20 or bank == 0x40 or bank == 0x60:
                # Select the next bank
                self.currBank = bank + 0x01
            else:
                self.currBank = bank

        elif 0x4000 <= loc < 0x6000:
            # RAM bank select
            self.eram_bank = data & 0b00000011

        elif 0x6000 <= loc < 0x8000:
            # Take the last bit and select the memory model
            self.memory_model = loc & 0x01

        elif loc < 0x9800:
            # Update the tile data
            self.tiles_outdated = True
            self.outdated_location = loc
            return self.vram[loc - 0x8000]
        elif loc < 0xA000:
            self.vram[loc - 0x8000] = data
        elif loc < 0xC000:
            # Holds the external ram available in the cart
            self.eram[loc - 0xA000 + (0x2000 * self.eram_bank)] = data
        elif loc < 0xE000:
            self.wram[loc - 0xC000] = data
        elif loc < 0xFE00:
            self.wram[loc - 0xE000] = data
        elif loc < 0xFEA0:
            self.oam[loc - 0xFE00] = data
        elif loc < 0xFF4C:
            self.io[loc - 0xFF00] = data
        elif loc < 0xFFFF:
            self.ram[loc - 0xFF80] = data

    # MBC2 Banking
    def write2(self, loc, data):
        if 0x0000 <= loc < 0x2000:
            if loc & 0x0A:
                self.disable_eram = False
            else:
                self.disable_eram = True

        elif 0x2000 <= loc < 0x4000:
            # Take 0bXXXXBBBB where B = bank select bits
            # This will select a bank for 0x4000 - 0x7FFF to map to in ROM
            bank = data & 0b00001111

            # Now map the bank on info we know
            # 0 and 1 map to bank 1

            # 0x20, 0x40 and 0x60 are unused, created 125 banks
            if bank == 0:
                self.currBank = 1
            elif bank == 0x20 or bank == 0x40 or bank == 0x60:
                # Select the next bank
                self.currBank = bank + 0x01
            else:
                self.currBank = bank

        elif 0x4000 <= loc < 0x6000:
            # RAM bank select
            self.eram_bank = data & 0b00000011

        elif 0x6000 <= loc < 0x8000:
            # Take the last bit and select the memory model
            # self.memory_model = loc & 0x01
            pass
        elif loc < 0x9800:
            # Update the tile data
            self.tiles_outdated = True
            self.outdated_location = loc
            return self.vram[loc - 0x8000]
        elif loc < 0xA000:
            self.vram[loc - 0x8000] = data
        elif loc < 0xC000:
            # Holds the external ram available in the cart
            self.eram[loc - 0xA000] = data
        elif loc < 0xE000:
            self.wram[loc - 0xC000] = data
        elif loc < 0xFE00:
            self.wram[loc - 0xE000] = data
        elif loc < 0xFEA0:
            self.oam[loc - 0xFE00] = data
        elif loc < 0xFF4C:
            self.io[loc - 0xFF00] = data
        elif loc < 0xFFFF:
            self.ram[loc - 0xFF80] = data

    # MBC3 Banking
    def write3(self, loc, data):
        if 0x0000 <= loc < 0x2000:
            if loc & 0x0A:
                self.disable_eram = False
                self.disable_rtc = False
            else:
                self.disable_eram = True
                self.disable_rtc = True

        elif 0x2000 <= loc < 0x4000:
            # Take 0bXXXBBBBB where B = bank select bits
            # This will select a bank for 0x4000 - 0x7FFF to map to in ROM
            bank = data

            # Now map the bank on info we know
            # 0 and 1 map to bank 1

            # 0x20, 0x40 and 0x60 are unused, created 125 banks
            if bank == 0:
                self.currBank = 1
            else:
                self.currBank = bank

        elif 0x4000 <= loc < 0x6000:
            # RAM bank select
            if data <= 3:
                self.eram_bank = data & 0x0F
                self.map_rtc = False
            else:
                self.map_rtc = True

        elif 0x6000 <= loc < 0x8000:
            # Writing 0x00 then 0x01, the current time is latched in the rtc registers
            if data == 0:
                self.latch_rtc = 1
            elif data == 1:
                self.latch_rtc = 2

                # Load the time from the OS clock
                date = datetime.now()
                self.seconds = date.second
                self.minutes = date.minute
                self.hours = date.hour
                self.days = date.day

        elif loc < 0x9800:
            # Update the tile data
            self.tiles_outdated = True
            self.outdated_location = loc
            return self.vram[loc - 0x8000]

        elif loc < 0xA000:
            self.vram[loc - 0x8000] = data
        elif loc < 0xC000:
            # Holds the external ram available in the cart
            self.eram[loc - 0xA000 + (0x2000 * self.eram_bank)] = data
        elif loc < 0xE000:
            self.wram[loc - 0xC000] = data
        elif loc < 0xFE00:
            self.wram[loc - 0xE000] = data
        elif loc < 0xFEA0:
            self.oam[loc - 0xFE00] = data
        elif loc < 0xFF4C:
            self.io[loc - 0xFF00] = data
        elif loc < 0xFFFF:
            self.ram[loc - 0xFF80] = data

    # MBC5 Banking
    def write5(self, loc, data):
        # Same as MBC1
        if 0x0000 <= loc < 0x2000:
            if loc & 0x0A:
                self.disable_eram = False
            else:
                self.disable_eram = True

        # Holds the lower 8 bits of the ROM bank number
        elif 0x2000 <= loc < 0x3000:
            self.currBank &= 0x00  # Remove the lower bits
            self.currBank |= data

        elif 0x3000 <= loc < 0x4000:
            self.currBank &= 0x0FF  # Remove the high bit
            self.currBank |= data << 8

        elif 0x4000 <= loc < 0x6000:
            # RAM bank select
            self.eram_bank = data & 0x0F

        elif 0x6000 <= loc < 0x8000:
            # Take the last bit and select the memory model
            self.memory_model = loc & 0x01

        elif loc < 0x9800:
            # Update the tile data
            self.tiles_outdated = True
            self.outdated_location = loc
            return self.vram[loc - 0x8000]

        elif loc < 0xA000:
            self.vram[loc - 0x8000] = data
        elif loc < 0xC000:
            # Holds the external ram available in the cart
            self.eram[loc - 0xA000 + (0x2000 * self.eram_bank)] = data
        elif loc < 0xE000:
            self.wram[loc - 0xC000] = data
        elif loc < 0xFE00:
            self.wram[loc - 0xE000] = data
        elif loc < 0xFEA0:
            self.oam[loc - 0xFE00] = data
        elif loc < 0xFF4C:
            self.io[loc - 0xFF00] = data
        elif loc < 0xFFFF:
            self.ram[loc - 0xFF80] = data

    def write(self, loc, data):
        # Map the bankingType to a dictionary function
        banking_functions = {
            0: self.write0,
            1: self.write1,
            2: self.write2,
            3: self.write3,
            5: self.write5
        }

        # Execute the appropriate banking function
        banking_functions[self.banking_type](loc, data)

    def read_rom(self, rom):
        # Put the ROM into memory
        stream = open(rom, "rb")

        rom_array = bytearray(stream.read())
        stream.close()

        # Firstly read the memory banking type
        cart_type = rom_array[0x147]

        # Now map this to a memory controller
        mbc0_values = [0x0, 0x8, 0x9, 0xB, 0xC, 0xD]
        mbc1_values = [0x1, 0x2, 0x3]
        mbc2_values = [0x5, 0x6]
        mbc3_values = [0x12, 0x13]
        mbc5_values = [0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E]

        if cart_type in mbc0_values:
            self.banking_type = 0
        elif cart_type in mbc1_values:
            self.banking_type = 1
        elif cart_type in mbc2_values:
            self.banking_type = 2
        elif cart_type in mbc3_values:
            self.banking_type = 3
        elif cart_type in mbc5_values:
            self.banking_type = 5
        else:
            # Set it to 0 and hope for the best...
            self.banking_type = 0

        # Place this in memory
        self.rom = rom_array

    def attach_gpu(self, gpu):
        self.gpu = gpu
