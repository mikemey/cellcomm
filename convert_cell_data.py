#!/usr/bin/env python3
import sys
import json
import os

OUTPUT_SUFFIX = 'coll.json'
BARCODES_SUFFIX = 'barcodes.tsv'
GENES_SUFFIX = 'genes.tsv'
MATRIX_SUFFIX = 'matrix.mtx'

print()
if len(sys.argv) < 2:
    print('parameter for matrix file missing!')
    exit(-1)

matrix_file = sys.argv[1]
sample_id = matrix_file.rstrip(MATRIX_SUFFIX)
genes_file = sample_id + GENES_SUFFIX
barcodes_file = sample_id + BARCODES_SUFFIX
output_file = sample_id + OUTPUT_SUFFIX

for in_file in [matrix_file, genes_file, barcodes_file]:
    if not os.path.exists(in_file):
        print('required file not found:', in_file)
        exit(-2)

if os.path.exists(output_file):
    overwrite = input(f'output file exists: "{output_file}", overwrite? [y/n] ').lower()
    if overwrite != 'y':
        print('aborted.')
        exit(0)


def import_file(file, converter, skip=0):
    result = []
    print(f'read "{file}" ... ', end='', flush=True)
    with open(file) as f:
        for line in f.readlines()[skip:]:
            result.append(converter(line))
    print('DONE')
    return result


def convert_matrix(barcodes_, genes_, matrix_):
    print(f'converting matrix to json ... ', end='', flush=True)
    current_id, cells, cell_record = 0, [], {}
    for gene_line_num, barcode_line_num, p_val in matrix_:
        if barcode_line_num != current_id:
            current_id = barcode_line_num
            cell_record = {
                '_id': barcode_line_num,
                'name': get_line_num(barcodes_, barcode_line_num),
                'genes': []
            }
            cells.append(cell_record)

        gene_symbols = get_line_num(genes_, gene_line_num)
        cell_record['genes'].append({
            'ensembl': gene_symbols[0],
            'mgi': gene_symbols[1],
            'pval': int(p_val)
        })
    print('DONE')
    return cells


def get_line_num(arr, ix):
    """ Barcode + genes references are 1-based
    """
    return arr[int(ix) - 1]


def store_json(cell_json):
    print(f'saving json ... ', end='', flush=True)
    with open(output_file, 'w') as outfile:
        json.dump(cell_json, outfile)
    print('DONE')


if __name__ == '__main__':
    barcodes = import_file(barcodes_file, lambda line: line.strip())
    genes = import_file(genes_file, lambda line: line.strip().split('\t'))
    matrix = import_file(matrix_file, lambda line: line.strip().split(' '), skip=3)

    print('barcodes:', len(barcodes))
    print('genes:', len(genes))
    print('matrix:', len(matrix))

    cell_data = convert_matrix(barcodes, genes, matrix)
    store_json(cell_data)
