from cpu import CPU
from gpu import GPU

import OpenGL.GLUT as glut
import OpenGL.GL as gl

import time

class GameBoy(object):
    def __init__(self):
        # Perform launch operations

        # Initialise the CPU
        self.cpu = CPU()
        self.gpu = GPU(self.cpu.memory)

        self.running = True

    def keyboard(self, key, x, y):
        pass

    def display(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glDrawArrays(gl.GL_QUAD_STRIP)
        glut.glutSwapBuffers()

    def reshape(self, width, height):
        gl.glViewport(0, 0, width, height)

    def init_window(self):
        glut.glutInit()
        glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
        glut.glutCreateWindow('PythonGB')
        glut.glutReshapeWindow(512, 512)
        glut.glutReshapeFunc(self.reshape)
        glut.glutDisplayFunc(self.display)
        glut.glutKeyboardFunc(self.keyboard)

    def run(self, rom_path):
        # Firstly load the ROM
        self.cpu.memory.read_rom(rom_path)

        while self.running:
            # Firstly execute an instruction
            self.cpu.executeOpcode(self.cpu.memory.read(self.cpu.r["pc"]))

            print("PC: " + str(hex(self.cpu.r["pc"])))

            # Increment the PC
            self.cpu.incPC()

            # Sync the GPU with the CPU
            self.gpu.sync(self.cpu.last_clock_inc)
