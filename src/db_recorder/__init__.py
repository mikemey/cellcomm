import os
from datetime import datetime

from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'cellcomm'
ENCODINGS_COLLECTION = 'encs'
ITERATIONS_COLLECTION = 'encits'
CELLS_COLLECTION = 'cells'


def get_file_name(full_path):
    return full_path.split('/')[-1]


def check_files(sources):
    for src_type in sources:
        src_file = sources[src_type]
        if not os.path.exists(src_file):
            raise ValueError(f'File for "{src_type}" not found: {src_file}')


class DbRecorder:
    def __init__(self, enc_run_id, sources, m_db=MONGO_DB):
        check_files(sources)
        self.enc_run_id = enc_run_id
        self.matrix_file = sources['matrix']
        self.barcodes_file = sources['barcodes']
        self.genes_file = sources['genes']
        self.db = MongoClient(MONGO_URL)[m_db]

        # data_id, barcode_file = convert_from(matrix_file_path)
        # self.cells = self.__load_cells(data_id, barcode_file)
        # print(self.cells)
        # self.__store_metadata(barcode_file_path)

    def __coll(self, coll_name) -> Collection:
        return self.db[coll_name]

    def __load_cells(self, data_id, barcode_file):
        cells = self.__coll(CELLS_COLLECTION)
        print('searching: ', data_id)
        query = {'_id': {'sid': data_id}}
        if cells.count_documents(query) == 0:
            print('would import barcodes:', barcode_file)
            # self.__insert_cells(barcode_file)
        return list(cells.find(query))

    def store_encoding_run(self):
        if self.__coll(ENCODINGS_COLLECTION).find_one({'_id': self.enc_run_id}):
            raise ValueError(f'Encoding run id already exists: {self.enc_run_id}')
        encoding = {
            '_id': self.enc_run_id,
            'date': datetime.now(),
            'defit': 0,
            'srcs': {
                'matrix': get_file_name(self.matrix_file),
                'barcodes': get_file_name(self.barcodes_file),
                'genes': get_file_name(self.genes_file)
            }
        }
        self.__coll(ENCODINGS_COLLECTION).insert_one(encoding)

    # def load_barcodes(data_source):
    #     barcode_file = data_source + BARCODE_FILE_EXT
    #     result = []
    #     with open(barcode_file) as f:
    #         for line in f.readlines():
    #             result.append(line.strip())
    #     return result

    # def save_encodings(self, trainer: CellTraining):
    #     def intercept(it, _):
    #         encodings = trainer.network.encoding_prediction(trainer.data)
    #
    #         encoding = {
    #             '_id': iteration_,
    #             'pids': ids,
    #             'ns': names,
    #             'xs': coords_[:, 0].tolist(),
    #             'ys': coords_[:, 1].tolist(),
    #             'zs': coords_[:, 2].tolist()
    #         }
    # self.encodings_coll.insert_one(encoding)
    #         with open(f'{self.encodings_dir}/{it}.enc', 'wb') as f:
    #             pickle.dump(encodings, f, protocol=pickle.HIGHEST_PROTOCOL)
    #
    #     return intercept
