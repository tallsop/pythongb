# Reference: http://imrannazar.com/GameBoy-Emulation-in-JavaScript:-GPU-Timings


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

    # This function syncs the GPU with the CPUs clock
    def sync(self, cycles):
        # We use a dictionary for speed
        self.clock += cycles

        if self.mode == 2:
            if self.clock >= 20:
                # Move to VRAM access mode
                self.mode = 3

                self.clock = 0

        elif self.mode == 3:
            if self.clock >= 43:
                self.mode = 0

            self.clock = 0

        elif self.mode == 0:
            if self.clock >= 51:
                self.clock = 0
                self.line += 1

                if self.line == 143:
                    # Perform a VBlank
                    self.mode = 0
                    self.line = 0
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


