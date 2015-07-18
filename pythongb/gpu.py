

class GPU(object):
    def __init__(self, mem_controller):
        # It needs to have access to main memory
        self.memory = mem_controller

    def render(self):
        pass
