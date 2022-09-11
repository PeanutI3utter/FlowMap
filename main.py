import sys

from stages.packing import gate_decomposition
from stages.bng import blif_to_bng
from stages.bng import bng_to_blif
from stages.label import label
from stages.mapping import flowmap


def main():
    if (len(sys.argv) != 3):
        print('Usage: python main.py [PATH_TO_BLIF] [k]')
        sys.exit()

    bng = blif_to_bng(sys.argv[1])
    name = bng.graph['name']
    lut = flowmap(label(bng, int(sys.argv[2])))
    print(len(lut.nodes))
    bng_to_blif(lut, 'a.blif', model_name=f'{name}_mapped')
    gate_decomposition(lut, int(sys.argv[2]))
    print(len(lut.nodes))
    bng_to_blif(lut, 'b.blif', model_name=f'{name}_mapped')


if __name__ == '__main__':
    main()
