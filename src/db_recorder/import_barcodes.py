from pymongo import MongoClient


def load_file(file, converter, skip=0):
    result = []
    print(f'loading "{file}" ... ', end='', flush=True)
    with open(file) as f:
        for line in f.readlines()[skip:]:
            result.append(converter(line))
    print(f'{len(result)} lines read')
    return result


def convert_matrix(source_id, barcodes, genes_src, matrix):
    def default_gene(e, m):
        return {'sid': source_id, 'e': e, 'm': m, 'cids': []}

    print(f'converting matrix ... ', end='', flush=True)
    current_id, cells, genes, cell_record = 0, [], {}, {}
    for gene_line_num, barcode_line_num, p_val in matrix:
        cell_id = int(barcode_line_num)
        if barcode_line_num != current_id:
            current_id = barcode_line_num
            cell_record = {
                'sid': source_id,
                'cid': cell_id,
                'n': barcodes[cell_id - 1],
                'g': []
            }
            cells.append(cell_record)

        gene_symbols = get_line_num(genes_src, gene_line_num)
        ensembl, mgi = gene_symbols[0], gene_symbols[1]
        cell_record['g'].append({
            'e': ensembl,
            'm': mgi,
            'v': int(p_val)
        })
        gene_record = genes.setdefault(ensembl, default_gene(ensembl, mgi))
        gene_record['cids'].append(cell_id)

    sort_cell_genes_by_value(cells)
    genes_list = [genes[k] for k in genes]
    print('DONE')
    return cells, genes_list


def sort_cell_genes_by_value(cells):
    for cell in cells:
        cell['g'].sort(key=lambda gene: gene['v'], reverse=True)


def get_line_num(arr, line_num):
    """ Barcode + genes references are 1-based
    """
    return arr[int(line_num) - 1]


def import_cells(cells_genes, mongo_url, mongo_db, cells_collection, genes_collection):
    cell_json, genes_json = cells_genes
    print(f'importing cells ... ', end='', flush=True)
    client = MongoClient(mongo_url)
    cells_coll = client[mongo_db][cells_collection]
    cells_coll.insert_many(cell_json)
    print('DONE')
    print(f'importing genes ... ', end='', flush=True)
    genes_coll = client[mongo_db][genes_collection]
    genes_coll.insert_many(genes_json)
    print('DONE')
    client.close()


def import_barcodes(source_id, matrix_file, barcodes_file, genes_file,
                    mongo_url, mongo_db, cells_collection, genes_collection):
    print('importing barcodes:', barcodes_file)
    matrix = load_file(matrix_file, lambda line: line.strip().split(' '), skip=3)
    barcodes = load_file(barcodes_file, lambda line: line.strip())
    genes = load_file(genes_file, lambda line: line.strip().split('\t'))

    cells_genes_data = convert_matrix(source_id, barcodes, genes, matrix)
    import_cells(cells_genes_data, mongo_url, mongo_db, cells_collection, genes_collection)
