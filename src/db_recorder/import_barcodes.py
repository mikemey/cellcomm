from pymongo import MongoClient


def load_file(file, converter, skip=0):
    result = []
    print(f'loading "{file}" ... ', end='', flush=True)
    with open(file) as f:
        for line in f.readlines()[skip:]:
            result.append(converter(line))
    print(f'{len(result)} lines read')
    return result


def convert_matrix(source_id, barcodes, genes, matrix):
    print(f'converting matrix ... ', end='', flush=True)
    current_id, cells, cell_record = 0, [], {}
    for gene_line_num, barcode_line_num, p_val in matrix:
        if barcode_line_num != current_id:
            current_id = barcode_line_num
            cell_id = int(barcode_line_num)
            cell_record = {
                'sid': source_id,
                'cid': cell_id,
                'n': barcodes[cell_id - 1],
                'g': []
            }
            cells.append(cell_record)

        gene_symbols = get_line_num(genes, gene_line_num)
        cell_record['g'].append({
            'e': gene_symbols[0],
            'm': gene_symbols[1],
            'v': int(p_val)
        })
    sort_cell_genes_by_value(cells)
    print('DONE')
    return cells


def sort_cell_genes_by_value(cells):
    for cell in cells:
        cell['g'].sort(key=lambda gene: gene['v'], reverse=True)


def get_line_num(arr, line_num):
    """ Barcode + genes references are 1-based
    """
    return arr[int(line_num) - 1]


def import_cells(cell_json, mongo_url, mongo_db, mongo_collection):
    print(f'importing cells ... ', end='', flush=True)
    client = MongoClient(mongo_url)
    cells_coll = client[mongo_db][mongo_collection]
    cells_coll.insert_many(cell_json)
    client.close()
    print('DONE')


def import_barcodes(source_id, matrix_file, barcodes_file, genes_file,
                    mongo_url, mongo_db, mongo_collection):
    print('importing barcodes:', barcodes_file)
    matrix = load_file(matrix_file, lambda line: line.strip().split(' '), skip=3)
    barcodes = load_file(barcodes_file, lambda line: line.strip())
    genes = load_file(genes_file, lambda line: line.strip().split('\t'))

    cell_data = convert_matrix(source_id, barcodes, genes, matrix)
    import_cells(cell_data, mongo_url, mongo_db, mongo_collection)
