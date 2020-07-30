import os
from db_recorder import DbRecorder, MONGO_URL, \
    ENCODINGS_COLLECTION, ITERATIONS_COLLECTION, CELLS_COLLECTION
from db_test import DbTestCase, TEST_DB
from datetime import datetime

TEST_RUN_ID = 'test-run'
TEST_BARCODE = 'example_barcodes.tsv'
TEST_BARCODE_PATH = os.path.join(os.path.dirname(__file__), TEST_BARCODE)


class DbRecorderCase(DbTestCase):
    def setUp(self):
        super().setUp()
        self.recorder = DbRecorder(TEST_RUN_ID, TEST_BARCODE_PATH, TEST_DB)

    def test_generator_train_model(self):
        self.recorder.store_encoding_run()
        enc_run = self._coll(ENCODINGS_COLLECTION).find_one({'_id': TEST_RUN_ID})
        self.assertEqual(enc_run['_id'], TEST_RUN_ID)
        age = datetime.now() - enc_run['date']
        self.assertLess(age.total_seconds(), 1)
        self.assertEqual(enc_run['defit'], 0)
        self.assertEqual(enc_run['src'], TEST_BARCODE)