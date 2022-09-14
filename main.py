import argparse
import networkx as nx
import time

from stages.enums import gate
from stages.bng import blif_to_bng
from stages.bng import bng_to_blif
from stages.label import label
from stages.mapping import flowmap
from stages.packing import gate_decomposition, flow_pack


def main():
    parser = argparse.ArgumentParser(
        description="Technology Mapping using FlowMap"
    )
    parser.add_argument(
        '-o',
        metavar='OUTPUT_FILE',
        type=str,
        help='Optional file output destination'
    )
    parser.add_argument(
        'blif',
        metavar='INPUT_BLIF',
        type=str,
        help='Path to BLIF file containing module to be mapped'
    )
    parser.add_argument(
        'k',
        metavar='K',
        type=int,
        help='Number of inputs in LUTs to be mapped'
    )
    args = parser.parse_args()

    k = args.k
    blif = args.blif

    t_start = time.time()
    bng = blif_to_bng(blif)
    name = bng.graph['name']
    if not args.o:
        output_file = f'{name}_mapped.blif'
    else:
        output_file = args.o

    t_bng = time.time()
    bng = label(bng, k)

    t_label = time.time()
    lut = flowmap(bng)

    lut_count_pre_opt = lut.number_of_nodes()
    lut_count_post_opt = lut_count_pre_opt

    t_flowmap = time.time()
    while True:
        gate_decomposition(lut, k)
        lut = flow_pack(lut, k)
        c_new = lut.number_of_nodes()

        if c_new >= lut_count_post_opt:
            break

        lut_count_post_opt = c_new

    bng_to_blif(lut, output_file, model_name=f'{name}_mapped')
    bng_to_blif(
        lut,
        output_file[:-5] + '_opt.blif',
        model_name=f'{name}_mapped_opt'
    )
    t_opt = time.time()

    outputs = [node for node, gtype in lut.nodes(data='gtype') if gtype == gate.PO]
    inputs = [node for node, gtype in lut.nodes(data='gtype') if gtype == gate.PI]

    max_depth = 0
    for input in inputs:
        for output in outputs:
            try:
                crit_path = max(nx.all_simple_paths(lut, input, output), key=len)
                depth = len(crit_path) - 1
                if depth > max_depth:
                    max_depth = depth
            except:
                pass

    print(
        'Mapping finished\n'
        f'Total time elapsed [s]: {t_opt - t_start}\n\n'
        f'Time [s] needed for\n'
        f'\tBNG creation: {t_bng - t_start}\n'
        f'\tLabel Phase: {t_label - t_bng}\n'
        f'\tMapping Phase: {t_flowmap - t_label}\n'
        f'\tOptimisations: {t_opt - t_flowmap}\n\n'

        f'Depth: {max_depth}\n\n'
        f'LUT counts:\n'
        f'\tPre optimisation: {lut_count_pre_opt}\n'
        f'\tPost optimisation: {lut_count_post_opt}\n'
    )


if __name__ == '__main__':
    main()
