import os
from datetime import datetime

from pymongo import MongoClient
from pymongo.collection import Collection

from db_recorder.import_barcodes import import_barcodes

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
        self.mongo_db = m_db
        self.source_id = None
        self.barcodes = None
        self.__db = MongoClient(MONGO_URL)[self.mongo_db]

    def __coll(self, coll_name) -> Collection:
        return self.__db[coll_name]

    def store_encoding_run(self):
        if self.__coll(ENCODINGS_COLLECTION).find_one({'_id': self.enc_run_id}):
            raise ValueError(f'Encoding run id already exists: {self.enc_run_id}')
        self.source_id = get_file_name(self.barcodes_file)
        encoding = {
            '_id': self.enc_run_id,
            'date': datetime.now(),
            'defit': 0,
            'srcs': {
                'matrix': get_file_name(self.matrix_file),
                'barcodes': self.source_id,
                'genes': get_file_name(self.genes_file)
            }
        }
        self.__coll(ENCODINGS_COLLECTION).insert_one(encoding)

    def load_barcodes(self):
        if not self.source_id:
            raise ValueError('Cannot load barcodes without encoding!')
        cells = self.__coll(CELLS_COLLECTION)
        query = {'sid': self.source_id}
        if cells.count_documents(query) == 0:
            import_barcodes(
                self.source_id, self.matrix_file, self.barcodes_file, self.genes_file,
                MONGO_URL, self.mongo_db, CELLS_COLLECTION
            )
        self.barcodes = list(cells.find(query, {'_id': 0}))

    def store_iteration(self):
        if not self.barcodes:
            raise ValueError('Cannot store iteration without barcodes!')
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
