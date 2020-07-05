import os
import unittest

import numpy as np
import tensorflow as tf

from cell_type_training import load_matrix, CellTraining, CellBigan

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'

TEST_TRAINING_FILE = os.path.join(os.path.dirname(__file__), 'example_matrix.mtx')
TEST_BATCH_SIZE = 3
TEST_GENE_COUNT = 11
TEST_MATRIX_CONTENT = [
    # gene: 32, 34, 39, 40, 60, 63, 23764, 27918, 27919, 27921, 27994
    [0, 0, 0, 0, 1, 11, 0, 0, 0, 6, 1],
    [0, 1, 0, 1, 0, 0, 0, 4, 0, 6, 0],
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 6, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 14, 0],
    [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
]


class TrainingTestCase(unittest.TestCase):
    def test_load_matrix_and_pivot(self):
        cell_batch = load_matrix(TEST_TRAINING_FILE)
        self.assertEqual((5, TEST_GENE_COUNT), cell_batch.shape)
        self.__assert_data(TEST_MATRIX_CONTENT, cell_batch)

    def test_sample_cell_data(self):
        cell_training = CellTraining(TEST_TRAINING_FILE, TEST_BATCH_SIZE)
        sampled = cell_training.sample_cell_data(0)
        self.assertEqual((TEST_BATCH_SIZE, TEST_GENE_COUNT), sampled.shape)
        self.__assert_data([TEST_MATRIX_CONTENT[2],
                            TEST_MATRIX_CONTENT[0],
                            TEST_MATRIX_CONTENT[1]], sampled)

    def __assert_data(self, expected, actual):
        eq_matrix = tf.math.equal(expected, actual)
        self.assertTrue(np.all(eq_matrix), f'\tExpected:\n{expected}\n\tActual:\n{actual}')

    def test_generator_model(self):
        cell_bigan = CellBigan(encoding_shape=(15,), gene_count=1000)
        generator = cell_bigan._generator
        self.assertEqual((None, 15), generator.input_shape)
        self.assertEqual((None, 1000), generator.output_shape)
        self.assertEqual(tf.nn.relu, generator.layers[-1].activation)
