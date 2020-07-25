#!/usr/bin/env python3
import os

import sys
from pymongo import MongoClient

BARCODES_SUFFIX = 'barcodes.tsv'
GENES_SUFFIX = 'genes.tsv'
MATRIX_SUFFIX = 'matrix.mtx'

MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'cellcomm'
MONGO_COLLECTION = 'cells'

if len(sys.argv) < 2:
    print('parameter for matrix file missing!')
    exit(-1)

matrix_file = sys.argv[1]
sample_id = matrix_file.rstrip(MATRIX_SUFFIX)
genes_file = sample_id + GENES_SUFFIX
barcodes_file = sample_id + BARCODES_SUFFIX

for in_file in [matrix_file, genes_file, barcodes_file]:
    if not os.path.exists(in_file):
        print('required file not found:', in_file)
        exit(-2)


def load_file(file, converter, skip=0):
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
                'n': get_line_num(barcodes_, barcode_line_num),
                'g': []
            }
            cells.append(cell_record)

        gene_symbols = get_line_num(genes_, gene_line_num)
        cell_record['g'].append({
            'e': gene_symbols[0],
            'm': gene_symbols[1],
            'v': int(p_val)
        })
    print('DONE')

    sort_cell_genes_by_value(cells)
    return cells


def sort_cell_genes_by_value(cells):
    for cell in cells:
        cell['g'].sort(key=lambda gene: gene['v'], reverse=True)


def get_line_num(arr, line_num):
    """ Barcode + genes references are 1-based
    """
    return arr[int(line_num) - 1]


def import_cells(cell_json):
    print(f'importing cells ... ', end='', flush=True)
    client = MongoClient(MONGO_URL)
    cells_coll = client[MONGO_DB][MONGO_COLLECTION]
    cells_coll.insert_many(cell_json)
    client.close()
    print('DONE')


if __name__ == '__main__':
    barcodes = load_file(barcodes_file, lambda line: line.strip())
    genes = load_file(genes_file, lambda line: line.strip().split('\t'))
    matrix = load_file(matrix_file, lambda line: line.strip().split(' '), skip=3)

    print('barcodes:', len(barcodes))
    print('genes:', len(genes))
    print('matrix:', len(matrix))

    cell_data = convert_matrix(barcodes, genes, matrix)
    import_cells(cell_data)
