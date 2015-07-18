from cpu import CPU


class GameBoy(object):
    def __init__(self):
        # Perform launch operations

        # Initialise the CPU
        self.cpu = CPU()

        self.running = True

    def run(self):
        while self.running:
            # Firstly execute an instruction
            self.cpu.executeOpcode(self.cpu.memory.read(self.cpu.r["pc"]))

            # Increment the PC
            self.cpu.incPC()

            # Service any interrupts
