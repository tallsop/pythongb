from pythongb.gb import GameBoy
import sys

if __name__ == "__main__":
    # Initialise a gameboy
    rom = sys.argv[0]

    gb = GameBoy()

    gb.run("tetris.gb")
