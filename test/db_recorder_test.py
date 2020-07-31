import os
from datetime import datetime
from unittest.mock import MagicMock

import numpy as np

from db_recorder import DbRecorder, ENCODINGS_COLLECTION, ITERATIONS_COLLECTION, CELLS_COLLECTION
from db_test import DbTestCase, TEST_DB


def relative_file(f_name):
    return os.path.join(os.path.dirname(__file__), f_name)


TEST_ENC_RUN_ID = 'test-run'
TEST_MATRIX = 'example_matrix.mtx'
TEST_BARCODES = 'example_barcodes.tsv'
TEST_GENES = 'example_genes.tsv'
TEST_SOURCES = {
    'matrix': relative_file(TEST_MATRIX),
    'barcodes': relative_file(TEST_BARCODES),
    'genes': relative_file(TEST_GENES)
}
UNUSED_DATA = {'what': 'ever'}


class DbRecorderCase(DbTestCase):
    def setUp(self):
        super().setUp()
        self.recorder = DbRecorder(TEST_ENC_RUN_ID, TEST_SOURCES, TEST_DB)

    def test_check_files(self):
        invalid_file = relative_file('does.not.exist')
        invalid_srcs = TEST_SOURCES.copy()
        invalid_srcs['barcodes'] = invalid_file
        with self.assertRaises(AssertionError) as cm:
            DbRecorder('fail-run-id', invalid_srcs)
        self.assertEqual(str(cm.exception), f'File not found: {invalid_file}')

    def test_stores_encoding_run(self):
        self.recorder.store_encoding_run()
        enc_run = self._coll(ENCODINGS_COLLECTION).find_one({'_id': TEST_ENC_RUN_ID})
        self.assertEqual(enc_run['_id'], TEST_ENC_RUN_ID)
        age = datetime.now() - enc_run['date']
        self.assertLess(age.total_seconds(), 1)
        self.assertEqual(enc_run['defit'], 0)
        self.assertEqual(enc_run['showits'], [0])
        db_srcs = enc_run['srcs']
        self.assertEqual(db_srcs['matrix'], TEST_MATRIX)
        self.assertEqual(db_srcs['barcodes'], TEST_BARCODES)
        self.assertEqual(db_srcs['genes'], TEST_GENES)

    def test_encoding_run_exists(self):
        self.recorder.store_encoding_run()
        with self.assertRaises(AssertionError) as cm:
            self.recorder.store_encoding_run()
        self.assertEqual(str(cm.exception), f'Encoding run id already exists: {TEST_ENC_RUN_ID}')

    def test_stores_barcodes_in_cells(self):
        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        cells = list(self._coll(CELLS_COLLECTION).find({'sid': TEST_BARCODES}))
        self.assertEqual(5, len(cells))
        self.__assert_cell(cells[0], 1, 'AAACCTGGTGTCCTCT-1', [
            {'e': 'ENSMUSG00000025902', 'm': 'Sox17', 'v': 11},
            {'e': 'ENSMUSG00000102343', 'm': 'Gm37381', 'v': 6},
            {'e': 'ENSMUSG00000089699', 'm': 'Gm1992', 'v': 1},
            {'e': 'ENSMUSG00000109048', 'm': 'Rp1', 'v': 1}
        ])
        self.__assert_cell(cells[4], 5, 'AAAGATGGTGATAAAC-1', [
            {'e': 'ENSMUSG00000109048', 'm': 'Rp1', 'v': 2}
        ])

    def __assert_cell(self, cell, expect_id, expect_name, expect_genes):
        self.assertEqual(TEST_BARCODES, cell['sid'])
        self.assertEqual(expect_id, cell['cid'])
        self.assertEqual(expect_name, cell['n'])
        for expect_gene, actual_gene in zip(expect_genes, cell['g']):
            self.assertDictEqual(expect_gene, actual_gene)

    def test_use_existing_barcodes_in_cells(self):
        name1, name2 = 'bla-bla', 'blu-blu'
        test_cells = [{'sid': TEST_BARCODES, 'n': name1}, {'sid': TEST_BARCODES, 'n': name2}]
        self._coll(CELLS_COLLECTION).insert_many(test_cells)

        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        self.assertEqual([name1, name2], self.recorder.barcodes)
        self.assertEqual([1, 2], self.recorder.cell_ids)

    def test_load_barcodes_without_store_encodings(self):
        with self.assertRaises(AssertionError) as cm:
            self.recorder.load_barcodes()
        self.assertIsNone(self.recorder.barcodes)
        self.assertEqual(str(cm.exception), f'Cannot load barcodes without encoding!')

    def test_create_interceptor_without_load_barcodes(self):
        with self.assertRaises(AssertionError) as cm:
            self.recorder.create_interceptor(None)
        self.assertEqual(str(cm.exception), f'Cannot store iterations without barcodes!')

    def test_intercept_stores_iteration(self):
        test_it = 2009
        test_encs = np.array([
            [0.5, 0.5, 0.0], [1.0, 0.2, 1.0], [0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5], [1.0, 0.2, 1.0]
        ])
        trainer_mock = MagicMock()
        trainer_mock.network.encoding_prediction = MagicMock(return_value=test_encs)
        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        self.recorder.create_interceptor(trainer_mock)(test_it, UNUSED_DATA)

        iteration = list(self._coll(ITERATIONS_COLLECTION).find(
            {'eid': TEST_ENC_RUN_ID, 'it': test_it}, {'_id': 0}
        ))
        self.assertEqual(1, len(iteration))
        self.assertDictEqual(iteration[0], {
            'eid': TEST_ENC_RUN_ID, 'it': test_it,
            'cids': [1, 2, 3, 4, 5],
            'ns': ['AAACCTGGTGTCCTCT-1', 'AAACGGGCAGGTCTCG-1', 'AAACGGGTCCGCTGTT-1', 'AAACGGGTCTGATTCT-1', 'AAAGATGGTGATAAAC-1'],
            'xs': [127.5, 255, 127.5, 127.5, 255],
            'ys': [127.5, 51, 127.5, 127.5, 51],
            'zs': [0.0, 255, 127.5, 127.5, 255],
            'ds': [[3, 4], [2, 5]]
        })

        encoding = self._coll(ENCODINGS_COLLECTION).find_one(
            {'_id': TEST_ENC_RUN_ID}, {'_id': 0, 'defit': 1}
        )
        self.assertEqual(test_it, encoding['defit'])

    def test_invalid_data_length_intercept(self):
        trainer_mock = MagicMock()
        test_data = np.array([[], [], [], []])
        trainer_mock.network.encoding_prediction = MagicMock(return_value=test_data)

        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        with self.assertRaises(AssertionError) as cm:
            self.recorder.create_interceptor(trainer_mock)(2, UNUSED_DATA)
        self.assertEqual(str(cm.exception), f'encodings + barcodes have different length: 4 != 5')

    def test_invalid_coord_length_intercept(self):
        trainer_mock = MagicMock()
        test_data = np.array([[1, 2], [1, 2], [1, 2], [1, 2], [1, 2]])
        trainer_mock.network.encoding_prediction = MagicMock(return_value=test_data)

        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        with self.assertRaises(AssertionError) as cm:
            self.recorder.create_interceptor(trainer_mock)(2, UNUSED_DATA)
        self.assertEqual(str(cm.exception), f'encodings vector length = 2, not in x, y, z format')

    def test_duplicate_iteration(self):
        test_it = 2009
        test_encs = np.array([
            [0.5, 0.5, 0.0], [1.0, 0.2, 1.0], [0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5], [1.0, 0.2, 1.0]
        ])
        trainer_mock = MagicMock()
        trainer_mock.network.encoding_prediction = MagicMock(return_value=test_encs)
        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        intercept = self.recorder.create_interceptor(trainer_mock)
        intercept(test_it, UNUSED_DATA)
        with self.assertRaises(AssertionError) as cm:
            intercept(test_it, UNUSED_DATA)
        self.assertEqual(str(cm.exception), f'duplicate iteration {test_it}')
