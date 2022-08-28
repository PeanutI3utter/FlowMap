import sys

from stages.bng import blif_to_bng
from stages.bng import subgraphToOnSet
from util.bngprint import print_bng


def main():
    if (len(sys.argv) != 3):
        print('Usage: python main.py [PATH_TO_BLIF] [k]')
        sys.exit()

    bng = blif_to_bng(sys.argv[1])
    print_bng(bng,3)
    print(subgraphToOnSet(bng))
    

if __name__ == '__main__':
    main()
