import unittest

import numpy as np

import cell_generator as cg


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
        self.__assert_cell_transcript(ctype.transcript_dists[0], 4869, 205)
        self.__assert_cell_transcript(ctype.transcript_dists[1], 9235, 221)

    def __assert_cell_transcript(self, transcript, mean, sd):
        self.assertEqual(transcript.mean, mean)
        self.assertEqual(transcript.sd, sd)
