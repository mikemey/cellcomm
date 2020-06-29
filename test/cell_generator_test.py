import unittest

import numpy as np

import cell_generator as cg
from cell_generator import CellType, TranscriptDistribution


class CellGenTest(unittest.TestCase):
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

    def test_generate_cell_record(self):
        np.random.seed(10)
        tc_labels = ['t1', 't2', 't3']
        transcripts = [TranscriptDistribution(tc_labels[0], 10, 2), TranscriptDistribution(tc_labels[2], 3, 1)]
        ctype = CellType('test', tc_labels, transcripts)
        record = ctype.generate_record(3)
        self.assertEqual('test,2,0,1', record)
        print(record)
