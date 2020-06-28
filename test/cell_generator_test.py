import unittest

import cell_generator as data_gen


class DataGenTest(unittest.TestCase):
    def test_generate_small_transcripts(self):
        tcs = data_gen.generate_transcripts(4)
        self.assertListEqual(['AAA', 'AAB', 'AAC', 'AAD'], tcs)

    def test_generate_large_transcripts(self):
        count = 2000
        tcs = data_gen.generate_transcripts(count)
        self.assertEqual(count, len(tcs))
        self.assertEqual('AAA', tcs[0])
        self.assertEqual('CYX', tcs[count - 1])

    def test_reject_too_many_transcripts(self):
        too_many = pow(26, 3) + 1
        with self.assertRaises(AssertionError) as ctx:
            data_gen.generate_transcripts(too_many)
        self.assertEqual(f'too many transcripts: {too_many}', str(ctx.exception))
