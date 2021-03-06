from pythongb.gb import GameBoy
from PIL import Image


def test_graphics():
    gb = GameBoy()

    gb.cpu.memory.read_rom("tetris.gb")

    # Now execute
    for i in range(10000):
        gb.cpu.executeOpcode(gb.cpu.memory.read(gb.cpu.r["pc"]))
        gb.cpu.r["pc"] += 1

    # Now get the tiles from memory
    gb.gpu.build_tile_data()

    print("Printing Tile Data\n\n")

    for tile in gb.gpu.tiles:
        for y in tile:
            for x in y:
                print(x)

if __name__ == "__main__":
    test_graphics()
