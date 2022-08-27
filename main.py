import sys

from stages.label import flowGraph
from stages.bng import blif_to_bng
from util.bngprint import print_bng


def main():
    if (len(sys.argv) != 3):
        print('Usage: python main.py [PATH_TO_BLIF] [k]')
        sys.exit()

    print_bng(blif_to_bng(sys.argv[1]), 3)
    

if __name__ == '__main__':
    main()