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
        self.map = Image.new("RGB", (256, 256), "white")

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

    def get_line(self):
        # Decide which map to use
        map_start = 0x9C00 if (self.memory.read(self.LCD_CONTROL) & 0b00001000) >> 3 == 1 else 0x9800

        # Read the appropriate line
        y_start = self.line

        # Read the line
        



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
                self.line += 1

                # Write the current line to the register
                self.memory.write(self.LCD_Y_LINE, self.line)

                if self.line == 143:
                    # Perform a VBlank
                    self.mode = 0
                    self.line = 0

                    # Push the image to be rendered
                    # TODO: Render the screen
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


