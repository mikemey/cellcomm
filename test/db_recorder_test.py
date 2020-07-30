import os
from db_recorder import DbRecorder, MONGO_URL, \
    ENCODINGS_COLLECTION, ITERATIONS_COLLECTION, CELLS_COLLECTION
from db_test import DbTestCase, TEST_DB
from datetime import datetime


def relative_file(f_name):
    return os.path.join(os.path.dirname(__file__), f_name)


TEST_RUN_ID = 'test-run'
TEST_MATRIX = 'example_matrix.mtx'
TEST_BARCODE = 'example_barcodes.tsv'
TEST_GENES = 'example_genes.tsv'
TEST_SOURCES = {
    'matrix': relative_file(TEST_MATRIX),
    'barcodes': relative_file(TEST_BARCODE),
    'genes': relative_file(TEST_GENES)
}


class DbRecorderCase(DbTestCase):
    def setUp(self):
        super().setUp()
        self.recorder = DbRecorder(TEST_RUN_ID, TEST_SOURCES, TEST_DB)

    def __find_encoding(self, run_id):
        return self._coll(ENCODINGS_COLLECTION).find_one({'_id': run_id})

    def test_check_files(self):
        invalid_file = relative_file('does.not.exist')
        invalid_srcs = TEST_SOURCES.copy()
        invalid_srcs['barcodes'] = invalid_file
        with self.assertRaises(ValueError) as cm:
            DbRecorder('fail-run-id', invalid_srcs)
        self.assertEqual(str(cm.exception), f'File for "barcodes" not found: {invalid_file}')

    def test_stores_encoding_run(self):
        self.recorder.store_encoding_run()
        enc_run = self.__find_encoding(TEST_RUN_ID)
        self.assertEqual(enc_run['_id'], TEST_RUN_ID)
        age = datetime.now() - enc_run['date']
        self.assertLess(age.total_seconds(), 1)
        self.assertEqual(enc_run['defit'], 0)
        db_srcs = enc_run['srcs']
        self.assertEqual(db_srcs['matrix'], TEST_MATRIX)
        self.assertEqual(db_srcs['barcodes'], TEST_BARCODE)
        self.assertEqual(db_srcs['genes'], TEST_GENES)

    def test_encoding_run_exists(self):
        self.recorder.store_encoding_run()
        with self.assertRaises(ValueError) as cm:
            self.recorder.store_encoding_run()
        self.assertEqual(str(cm.exception), f'Encoding run id already exists: {TEST_RUN_ID}')
