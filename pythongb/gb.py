from .gpu import GPU
from .cpu import CPU
from .memory import MemoryController

import OpenGL.GLUT as glut
import OpenGL.GL as gl
import numpy as np
from vispy import app, gloo

import time

class GameBoy(object):
    class GBCanvas(app.Canvas):
        def __init__(self):
            self.vertex_shader = """
                attribute vec2 position;
                attribute vec2 texcoord;
                varying vec2 v_texcoord;
                void main()
                {
                    gl_Position = vec4(position, 0.0, 1.0);
                    v_texcoord = texcoord;
                }
            """

            self.fragment_shader = """
                uniform sampler2D texture;
                varying vec2 v_texcoord;
                void main()
                {
                    vec3 clr = texture2D(texture, v_texcoord).rgb;
                    gl_FragColor.rgb = clr;
                    gl_FragColor.a = 1.0;
                }
            """

            self.texture = np.zeros((160, 144, 3), dtype=np.float32)

            app.Canvas.__init__(self, size=(160, 148), keys="interactive", show=True)

            self.program = gloo.Program(self.vertex_shader, self.fragment_shader, count=4)
            self.program['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
            self.program['texcoord'] = [(0, 1), (0, 0), (1, 1), (1, 0)]

            self.program['texture'] = self.texture

        def set_frame(self, texture):
            self.texture = texture
            self.program["texture"] = texture

            self.update()

        def on_draw(self, event):
            gloo.clear(color=True, depth=True)
            self.program.draw("triangle_strip")

    def __init__(self, debug):
        # Perform launch operations
        self.cpu = CPU(debug)
        self.gpu = GPU(self.cpu.memory)

        self.cpu.memory.attach_gpu(self.gpu)

        # Holds a frame to be rendered to the window
        self.frame = np.zeros([160, 144], dtype=np.uint8)

        self.running = True

        self.debug = debug

    def run(self, rom_path):
        # Firstly load the ROM
        self.cpu.memory.read_rom(rom_path)

        # Setup a canvas
        canvas = GameBoy.GBCanvas()

        app.run()

        while self.running:
            # Increment the PC
            if self.debug:
                print("Exec PC: " + str(hex(self.cpu.r["pc"])))

            # Firstly execute an instruction
            self.cpu.executeOpcode(self.cpu.memory.read(self.cpu.r["pc"]))

            # Sync the GPU with the CPU
            self.gpu.sync(self.cpu.last_clock_inc)

            # Get a frame if it is ready
            frame = self.gpu.get_frame()

            if frame is not None:
                # Place the frame into the current
                canvas.set_frame(frame)

            self.cpu.incPC()