import os
import shutil
import unittest
from types import GeneratorType

import numpy as np

import cell_generator as cg
from cell_generator import CellType, TranscriptDistribution

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
GENERATED_TEST_FILE = os.path.join(TEST_DATA_DIR, 'test-file.csv')
EXPECTED_TEST_FILE = os.path.join(os.path.dirname(__file__), 'cell_generator_expected.csv')


class CellGenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
        os.mkdir(TEST_DATA_DIR)

    def test_generate_small_transcript_labels(self):
        tcs = cg.generate_transcript_labels(4)
        self.assertListEqual(['AAA', 'AAB', 'AAC', 'AAD'], tcs)

    def test_generate_large_transcript_labels(self):
        count = 2000
        tcs = cg.generate_transcript_labels(count)
        self.assertEqual(count, len(tcs))
        self.assertEqual('AAA', tcs[0])
        self.assertEqual('CYX', tcs[count - 1])

    def test_reject_too_many_transcript_labels(self):
        too_many = pow(26, 3) + 1
        with self.assertRaises(AssertionError) as ctx:
            cg.generate_transcript_labels(too_many)
        self.assertEqual(f'too many transcripts: {too_many}', str(ctx.exception))

    def test_generate_cell_type(self):
        np.random.seed(0)
        tcs = cg.generate_transcript_labels(5)
        name = 'test-type'

        ctype = cg.generate_cell_type(
            name, tcs, expressed_ratio=0.6, dist_range=(10, 10000), dist_variance=(10, 400)
        )
        self.assertEqual(name, ctype.name)
        self.assertEqual(tcs, ctype.transcript_labels)
        self.__assert_transcript_type(ctype.transcript_dists[0], 'AAC', 4869, 205)
        self.__assert_transcript_type(ctype.transcript_dists[1], 'AAA', 9235, 221)

    def __assert_transcript_type(self, transcript, label, mean, sd):
        self.assertEqual(label, transcript.label)
        self.assertEqual(mean, transcript.mean)
        self.assertEqual(sd, transcript.sd)

    def test_generate_csv_header(self):
        labels = cg.generate_transcript_labels(5)
        header = cg.generate_csv_header(labels)
        self.assertEqual('cell_type,AAA,AAB,AAC,AAD,AAE\n', header)

    def test_generate_csv_cell_record(self):
        np.random.seed(6)
        tc_labels = ['t1', 't2', 't3']
        transcripts = [TranscriptDistribution(tc_labels[0], 10, 2), TranscriptDistribution(tc_labels[2], 3, 1)]
        ctype = CellType('test', tc_labels, transcripts)
        record = ctype.generate_csv_record(3)
        self.assertEqual('test,2,0,1\n', record)

    def test_generate_full_example(self):
        np.random.seed(0)
        labels = cg.generate_transcript_labels(50)
        records = cg.generate_csv_records(
            records_count=10,
            transcripts_count=20,
            cell_types=[
                cg.generate_cell_type('c1', labels, 0.2, (100, 1000), (10, 100)),
                cg.generate_cell_type('c2', labels, 0.25, (120, 2000), (50, 500)),
                cg.generate_cell_type('c3', labels, 0.15, (20, 500), (20, 100))
            ])
        self.assertEqual(GeneratorType, type(records))
        record_list = list(records)
        self.assertEqual(10, len(record_list))
        for actual, expected in zip(record_list, ['c3', 'c3', 'c1', 'c3', 'c2', 'c3', 'c1', 'c3', 'c1', 'c2']):
            self.assertEqual(actual[:2], expected)

    def test_write_file(self):
        np.random.seed(0)
        cg.generate_to_file(GENERATED_TEST_FILE, 2, 3, 2)
        with open(GENERATED_TEST_FILE) as f:
            content = f.read()
        self.assertEqual('cell_type,AAA,AAB,AAC\nc01,0,0,2\nc07,0,0,2\n', content)
