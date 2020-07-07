import os
from unittest.mock import MagicMock

from cell_type_training import load_matrix, CellTraining
from tf_testcase import TFTestCase

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'

TEST_TRAINING_FILE = os.path.join(os.path.dirname(__file__), 'example_matrix.mtx')
TEST_BATCH_SIZE = 3
TEST_GENE_COUNT = 11
TEST_ENCODING_SIZE = 8
TEST_MATRIX_CONTENT = [
    # gene: 32, 34, 39, 40, 60, 63, 23764, 27918, 27919, 27921, 27994
    [0, 0, 0, 0, 1, 11, 0, 0, 0, 6, 1],
    [0, 1, 0, 1, 0, 0, 0, 4, 0, 6, 0],
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 6, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 14, 0],
    [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
]


class CellTrainingTestCase(TFTestCase):
    def setUp(self):
        self.trainer = CellTraining('test-run', TEST_TRAINING_FILE, TEST_BATCH_SIZE,
                                    TEST_ENCODING_SIZE, write_log=False)
        self.trainer.sink = self.sink_mock = MagicMock()

    def test_load_matrix_and_pivot(self):
        cell_batch = load_matrix(TEST_TRAINING_FILE)
        self.assertEqual((5, TEST_GENE_COUNT), cell_batch.shape)
        self.assertDeepEqual(TEST_MATRIX_CONTENT, cell_batch)

    def test_sample_cell_data(self):
        sampled = self.trainer._sample_cell_data(0)
        self.assertEqual((TEST_BATCH_SIZE, TEST_GENE_COUNT), sampled.shape)
        self.assertDeepEqual([TEST_MATRIX_CONTENT[2],
                              TEST_MATRIX_CONTENT[0],
                              TEST_MATRIX_CONTENT[1]], sampled)

    def test_bigan_setup(self):
        bigan = self.trainer.bigan
        self.assertEqual(TEST_ENCODING_SIZE, bigan.encoding_size)
        self.assertEqual((None, TEST_ENCODING_SIZE), bigan._generator.input_shape)
        self.assertEqual((None, TEST_GENE_COUNT), bigan._generator.output_shape)

    def test_trainings_run(self):
        test_data, test_losses = ['some', 'data'], (0.7, 0.8, 0.8)
        self.trainer._sample_cell_data = sample_mock = MagicMock(return_value=test_data)
        self.trainer.bigan.trainings_step = trainings_step_mock = MagicMock(return_value=test_losses)

        test_iterations = 6
        self.trainer.run(test_iterations)
        self.assertEqual(sample_mock.call_count, test_iterations)
        trainings_step_mock.assert_called_with(test_data)
        self.assertEqual(trainings_step_mock.call_count, test_iterations)

        self.assertEqual(self.sink_mock.add_losses.call_count, test_iterations)
        self.sink_mock.add_losses.assert_called_with(5, 2.3, *test_losses)
        self.assertEqual(self.sink_mock.drain_data.call_count, 1)
