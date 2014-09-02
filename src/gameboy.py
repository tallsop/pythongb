import cpu, memory, graphics, sound

# Setup the pygame stuff
gbMem = memory.MemoryController()

gbMem.readROM("../poke.gb")

gbCPU = cpu.CPU(gbMem) # Pass the memory controller in

gbCPU.execute()
gbCPU.execute()