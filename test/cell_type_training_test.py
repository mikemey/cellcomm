import os
import unittest

import numpy as np
import tensorflow as tf

from cell_type_training import CellTraining, load_matrix

TEST_TRAINING_FILE = os.path.join(os.path.dirname(__file__), 'example_matrix.mtx')
TEST_BATCH_SIZE = 3
TEST_MATRIX_CONTENT = [
    # gene: 32, 34, 39, 40, 60, 63, 23764, 27918, 27919, 27921, 27994
    [0, 0, 0, 0, 1, 11, 0, 0, 0, 6, 1],
    [0, 1, 0, 1, 0, 0, 0, 4, 0, 6, 0],
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 6, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 14, 0],
    [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
]


class TrainingTestCase(unittest.TestCase):
    def setUp(self):
        self.cell_training = CellTraining(TEST_TRAINING_FILE, TEST_BATCH_SIZE)

    def test_load_matrix_and_pivot(self):
        cell_batch = load_matrix(TEST_TRAINING_FILE)
        print(cell_batch)
        self.assertEqual((5, 11), cell_batch.shape)
        self.__assert_data(TEST_MATRIX_CONTENT, cell_batch)

    # def test_sample_cell_data(self):
    #     pass
    #

    def __assert_data(self, expected, actual):
        eq_matrix = tf.math.equal(expected, actual)
        self.assertTrue(np.all(eq_matrix), f'\tExpected:\n{expected}\n\tActual:\n{actual}')
