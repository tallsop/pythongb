from cpu import CPU
from gpu import GPU


class GameBoy(object):
    def __init__(self):
        # Perform launch operations

        # Initialise the CPU
        self.cpu = CPU()
        self.gpu = GPU(self.cpu.memory)

        self.running = True

    def run(self):
        # Firstly load the ROM

        while self.running:
            # Firstly execute an instruction
            self.cpu.executeOpcode(self.cpu.memory.read(self.cpu.r["pc"]))

            # Increment the PC
            self.cpu.incPC()

            # Sync the GPU with the CPU
            self.gpu.sync(self.cpu.last_clock_inc)