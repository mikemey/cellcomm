import os
from datetime import datetime

import numpy as np
from pymongo import MongoClient
from pymongo.collection import Collection

from db_recorder.import_barcodes import import_barcodes

MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'cellcomm-update'
ENCODINGS_COLLECTION = 'encs'
ITERATIONS_COLLECTION = 'encits'
CELLS_COLLECTION = 'cells'
GENES_COLLECTION = 'genes'


def get_file_name(full_path):
    return full_path.split('/')[-1]


def check_files(sources):
    for src in sources:
        assert os.path.exists(src), f'File not found: {src}'


class DbRecorder:
    def __init__(self, enc_run_id, sources, m_db=MONGO_DB):
        self.enc_run_id = enc_run_id
        self.matrix_file = sources['matrix']
        self.barcodes_file = sources['barcodes']
        self.genes_file = sources['genes']
        check_files([self.matrix_file, self.barcodes_file, self.genes_file])
        self.mongo_db = m_db
        self.source_id = None
        self.barcodes = None
        self.cell_ids = None
        self.__db = MongoClient(MONGO_URL)[self.mongo_db]
        self.__processed_its = []

    def __coll(self, coll_name) -> Collection:
        return self.__db[coll_name]

    def store_encoding_run(self):
        assert self.__coll(ENCODINGS_COLLECTION).find_one({'_id': self.enc_run_id}) is None, \
            f'Encoding run id already exists: {self.enc_run_id}'

        self.source_id = get_file_name(self.barcodes_file)
        encoding = {
            '_id': self.enc_run_id,
            'date': datetime.now(),
            'defit': 0,
            'showits': [0],
            'srcs': {
                'matrix': get_file_name(self.matrix_file),
                'barcodes': self.source_id,
                'genes': get_file_name(self.genes_file)
            }
        }
        self.__coll(ENCODINGS_COLLECTION).insert_one(encoding)

    def load_barcodes(self):
        assert self.source_id, 'Cannot load barcodes without encoding!'
        cells = self.__coll(CELLS_COLLECTION)
        query = {'sid': self.source_id}
        if cells.count_documents(query) == 0:
            import_barcodes(
                self.source_id, self.matrix_file, self.barcodes_file, self.genes_file,
                MONGO_URL, self.mongo_db, CELLS_COLLECTION, GENES_COLLECTION
            )
        self.barcodes = [cell['n'] for cell in cells.find(query, {'_id': 0, 'n': 1})]
        self.cell_ids = [cell_id_from(i) for i in range(len(self.barcodes))]

    def create_interceptor(self, trainer):
        assert self.barcodes, 'Cannot store iterations without barcodes!'

        def intercept(it, _):
            assert it not in self.__processed_its, f'duplicate iteration {it}'
            self.__processed_its.append(it)
            encodings = trainer.network.encoding_prediction(trainer.data)
            enc_shape = encodings.shape
            assert enc_shape[0] == len(self.barcodes), \
                f'encodings + barcodes have different length: {enc_shape[0]} != {len(self.barcodes)}'
            assert enc_shape[1] == 3, \
                f'encodings vector length = {enc_shape[1]}, not in x, y, z format'

            coords = np.multiply(encodings, 255)
            self.__coll(ITERATIONS_COLLECTION).insert_one({
                'eid': self.enc_run_id,
                'it': it,
                'cids': self.cell_ids,
                'ns': self.barcodes,
                'xs': coords[:, 0].tolist(),
                'ys': coords[:, 1].tolist(),
                'zs': coords[:, 2].tolist(),
                'ds': find_duplicate_ids(coords)
            })
            self.__coll(ENCODINGS_COLLECTION).update_one(
                {'_id': self.enc_run_id}, {'$set': {'defit': it}}
            )

        return intercept


def find_duplicate_ids(np_coords: np.array):
    coords = [(c[0], c[1], c[2]) for c in np_coords]
    unique_coords = set(coords)
    all_indices = [[cell_id_from(i) for i, x in enumerate(coords) if x == uc] for uc in unique_coords]
    return [ixs for ixs in all_indices if len(ixs) > 1]


def cell_id_from(ix):
    return ix + 1
