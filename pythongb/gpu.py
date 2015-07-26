# Reference: http://imrannazar.com/GameBoy-Emulation-in-JavaScript:-GPU-Timings
from utils import *
from PIL import Image


class GPU(object):
    def __init__(self, mem_controller):
        # It needs to have access to main memory
        self.memory = mem_controller

        self.clock = 0

        # Holds the current mode for the CPU defined below:
        # 0 - HBlank, drawing of a line (51 Clocks)
        # 1 - VBlank, when all the lines are drawn, in this case, the image will be pushed to the screen (114 Clocks)
        # 2 - Scanline (Accessing OAM) (20 Clocks)
        # 3 - Scanline (Accessing VRAM) (43 Clocks)
        self.mode = 0

        # Holds the current line that would be drawn to
        self.line = 0

        # Create a 256 x 256 map for the bitmap
        self.map = Image.new("RGB", (160, 144), "white")

        # GPU Register locations in memory
        self.LCD_CONTROL = 0xFF40
        self.LCD_STATUS = 0xFF41

        self.SCROLL_Y = 0xFF42
        self.SCROLL_X = 0xFF43

        self.LCD_Y_LINE = 0xFF44
        self.LY_COMPARE = 0xFF45

        self.WINDOW_Y = 0xFF4A

        # The X position - 7
        self.WINDOW_X = 0xFF4B

        self.PALETTE = 0xFF47
        self.PALETTE0_DATA = 0xFF48
        self.PALETTE1_DATA = 0xFF49

        self.DMA_CONTROL = 0xFF46

        # Palette to colour map
        self.palette_map = {
            0: (255, 255, 255, 1),
            1: (192, 192, 192, 1),
            2: (96, 96, 96, 1),
            3: (0, 0, 0, 1)
        }

    # Returns a tile line as an array of coloured pixels
    def read_tile_line(self, tile, map_start, y):
        tile_start = tile * 16
        y_start = y * 2

        top = self.memory.read(map_start + tile_start + y_start)
        bottom = self.memory.read(map_start + tile_start + y_start + 1)

        tile = []

        for i in range(8):
            mask = 0b10000000 >> i
            pixel = ((bottom & mask) >> 7 - i) << 1 | (top & mask) >> 7 - i

            tile.append(self.palette_map[pixel])

        return tile

    def get_line(self):
        # Define the palette map
        pal = self.memory.read(self.PALETTE)
        palette = (pal & 0b11, (pal & 0b1100) >> 2, (pal & 0b110000) >> 4, (pal & 0b11000000) >> 6)

        # First decide if the window is being used or not
        window = True if (self.memory.read(self.LCD_CONTROL) & 0b00100000) >> 5 == 1 else False

        if window:
            tile_map_start = 0x8C00 if (self.memory.read(self.LCD_CONTROL) & 0b00001000) >> 3 == 1 else 0x9800
        else:
            tile_map_start = None

        # Decide which map to use
        map_start = 0x8C00 if (self.memory.read(self.LCD_CONTROL) & 0b00001000) >> 3 == 1 else 0x9800

        # Read the appropriate line
        y_start = self.line

        # Also need to adjust to the LCD x and y shift
        y_offset = ((y_start + self.memory.read(self.SCROLL_Y)) >> 3) << 5
        x_offset = self.memory.read(self.SCROLL_X) >> 3

        # Now read a tile
        tile = self.memory.read(map_start + y_offset + x_offset)

        # Since the window tiles are -128 - 128 map to 0 - 255
        if window:
            if tile >= 128:
                tile -= 128
            elif tile < 128:
                tile += 128

        x = x_offset

        # Read the line
        for i in xrange(160):
            loaded_tile = self.read_tile_line(tile, tile_map_start, self.line)
            self.map[x, self.line] = loaded_tile[x]

            x += 1

            if x == 8:
                x = 0
                y_offset += 1

                window = True if (self.memory.read(self.LCD_CONTROL) & 0b00100000) >> 5 == 1 else False

                if window:
                    tile_map_start = 0x8C00 if (self.memory.read(self.LCD_CONTROL) & 0b00001000) >> 3 == 1 else 0x9800
                else:
                    tile_map_start = None

                tile = self.memory.read(map_start + y_offset + x_offset)

                if window:
                    if tile >= 128:
                        tile -= 128
                    elif tile < 128:
                        tile += 128


    # This function syncs the GPU with the CPUs clock
    def sync(self, cycles):
        # Load the LCD Status Register

        self.clock += cycles

        # Read the status
        stat = self.memory.read(self.LCD_STATUS)
        self.mode = stat & 0x03

        if self.mode == 2:
            if self.clock >= 20:
                # Move to VRAM access mode
                self.mode = 3

                self.clock = 0

        elif self.mode == 3:
            if self.clock >= 43:
                self.mode = 0

                # Write a line to the frame buffer
                self.get_line()

            self.clock = 0

        elif self.mode == 0:
            if self.clock >= 51:
                self.clock = 0

                # Draw a line!
                self.get_line()

                self.line += 1
                # Write the current line to the register
                self.memory.write(self.LCD_Y_LINE, self.line)



                if self.line == 143:
                    # Perform a VBlank
                    self.mode = 0
                    self.line = 0

                    # Push the image to be rendered
                    # For testing purposes, just place it in a PIL container
                    map.show()
                else:
                    # Move to VRAM access
                    self.mode = 2

        else:
            if self.clock >= 114:
                self.clock = 0

                self.line += 1

                if self.line == 10:
                    self.line = 0
                    self.mode = 2

        # Write the status into memory
        self.memory.write(self.LCD_STATUS, (stat & 0xb11111100) | self.mode)


