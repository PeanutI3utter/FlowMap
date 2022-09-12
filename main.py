import sys

from stages.packing import gate_decomposition, flow_pack
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
    lut_c = lut.number_of_nodes()
    print(lut_c)
    bng_to_blif(lut, f'{name}_mapped.blif', model_name=f'{name}_mapped')
    while True:
        gate_decomposition(lut, int(sys.argv[2]))
        lut = flow_pack(lut, int(sys.argv[2]))
        c_new = lut.number_of_nodes()

        if c_new >= lut_c:
            break

        lut_c = c_new

    bng_to_blif(
        lut,
        f'{name}_mapped_opt.blif',
        model_name=f'{name}_mapped_opt'
    )
    print(lut_c)


if __name__ == '__main__':
    main()
