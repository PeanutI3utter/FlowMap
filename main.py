import sys

from stages.bng import blif_to_bng
from stages.bng import bng_to_blif
from stages.label import label
from stages.mapping import flowmap


def main():
    if (len(sys.argv) != 3):
        print('Usage: python main.py [PATH_TO_BLIF] [k]')
        sys.exit()

    bng = blif_to_bng(sys.argv[1])
    lut = flowmap(label(bng, int(sys.argv[2])))
    bng_to_blif(lut)
    

if __name__ == '__main__':
    main()
