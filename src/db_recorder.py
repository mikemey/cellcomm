from datetime import datetime
import os

from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'cellcomm'
ENCODINGS_COLLECTION = 'encs'
ITERATIONS_COLLECTION = 'encits'
CELLS_COLLECTION = 'cells'


class DbRecorder:
    def __init__(self, enc_run_id, barcode_file_path, m_db=MONGO_DB):
        self.enc_run_id = enc_run_id
        self.barcode_file = barcode_file_path
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
        src_id = self.barcode_file.split('/')[-1]
        encoding = {
            '_id': self.enc_run_id,
            'date': datetime.now(),
            'defit': 0,
            'src': src_id
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


if __name__ == '__main__':
    m = os.path.join(os.path.dirname(__file__), '..', 'data', 'GSE122930_TAC_4_weeks_small_matrix.mtx')
    r = DbRecorder('test-run-id', m)
