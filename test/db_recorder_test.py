import os
from db_recorder import DbRecorder, \
    ENCODINGS_COLLECTION, ITERATIONS_COLLECTION, CELLS_COLLECTION
from db_test import DbTestCase, TEST_DB
from datetime import datetime


def relative_file(f_name):
    return os.path.join(os.path.dirname(__file__), f_name)


TEST_RUN_ID = 'test-run'
TEST_MATRIX = 'example_matrix.mtx'
TEST_BARCODES = 'example_barcodes.tsv'
TEST_GENES = 'example_genes.tsv'
TEST_SOURCES = {
    'matrix': relative_file(TEST_MATRIX),
    'barcodes': relative_file(TEST_BARCODES),
    'genes': relative_file(TEST_GENES)
}


class DbRecorderCase(DbTestCase):
    def setUp(self):
        super().setUp()
        self.recorder = DbRecorder(TEST_RUN_ID, TEST_SOURCES, TEST_DB)

    def test_check_files(self):
        invalid_file = relative_file('does.not.exist')
        invalid_srcs = TEST_SOURCES.copy()
        invalid_srcs['barcodes'] = invalid_file
        with self.assertRaises(ValueError) as cm:
            DbRecorder('fail-run-id', invalid_srcs)
        self.assertEqual(str(cm.exception), f'File for "barcodes" not found: {invalid_file}')

    def test_stores_encoding_run(self):
        self.recorder.store_encoding_run()
        enc_run = self._coll(ENCODINGS_COLLECTION).find_one({'_id': TEST_RUN_ID})
        self.assertEqual(enc_run['_id'], TEST_RUN_ID)
        age = datetime.now() - enc_run['date']
        self.assertLess(age.total_seconds(), 1)
        self.assertEqual(enc_run['defit'], 0)
        db_srcs = enc_run['srcs']
        self.assertEqual(db_srcs['matrix'], TEST_MATRIX)
        self.assertEqual(db_srcs['barcodes'], TEST_BARCODES)
        self.assertEqual(db_srcs['genes'], TEST_GENES)

    def test_encoding_run_exists(self):
        self.recorder.store_encoding_run()
        with self.assertRaises(ValueError) as cm:
            self.recorder.store_encoding_run()
        self.assertEqual(str(cm.exception), f'Encoding run id already exists: {TEST_RUN_ID}')

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
        test_cells = {'sid': TEST_BARCODES, 'x': 'bla-bla'}
        self._coll(CELLS_COLLECTION).insert_one(test_cells)
        del test_cells['_id']

        self.recorder.store_encoding_run()
        self.recorder.load_barcodes()
        self.assertEqual(test_cells, self.recorder.barcodes[0])

    def test_load_barcodes_without_store_encodings(self):
        with self.assertRaises(ValueError) as cm:
            self.recorder.load_barcodes()
        self.assertIsNone(self.recorder.barcodes)
        self.assertEqual(str(cm.exception), f'Cannot load barcodes without encoding!')

    def test_store_without_load_barcodes(self):
        with self.assertRaises(ValueError) as cm:
            self.recorder.store_iteration()
        self.assertEqual(str(cm.exception), f'Cannot store iteration without barcodes!')
