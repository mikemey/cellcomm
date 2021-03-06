import os
from unittest.mock import MagicMock

from cell_type_training import load_matrix, load_cells, CellTraining
from tf_testcase import TFTestCase

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'

TEST_MATRIX_FILE = os.path.join(os.path.dirname(__file__), 'example_matrix.mtx')
TEST_BATCH_SIZE = 3
TEST_GENE_COUNT = 5
TEST_ENCODING_SIZE = 8
TEST_BATCHES_PER_ITERATION = 4
TEST_MATRIX_CONTENT = [
    # gene: 1, 2, 3, 4, 5
    [0, 1, 6, 1, 11],
    [4, 1, 0, 1, 6],
    [1, 1, 1, 1, 6],
    [1, 0, 14, 0, 1],
    [0, 0, 0, 2, 0],
]


class CellTrainingTestCase(TFTestCase):
    def setUp(self):
        self.cell_batch = load_matrix(TEST_MATRIX_FILE)
        self.trainer = CellTraining(
            self.cell_batch, TEST_BATCH_SIZE, TEST_ENCODING_SIZE,
            batches_per_iteration=TEST_BATCHES_PER_ITERATION
        )

    def test_load_matrix_and_pivot(self):
        self.assertEqual((5, TEST_GENE_COUNT), self.cell_batch.shape)
        self.assertDeepEqual(TEST_MATRIX_CONTENT, self.cell_batch)

    def test_sample_cell_data(self):
        sampled = self.trainer.sample_cell_data(0)
        self.assertEqual((TEST_BATCH_SIZE, TEST_GENE_COUNT), sampled.shape)
        self.assertDeepEqual([TEST_MATRIX_CONTENT[2],
                              TEST_MATRIX_CONTENT[0],
                              TEST_MATRIX_CONTENT[1]], sampled)

    def test_bigan_setup(self):
        bigan = self.trainer.network
        self.assertEqual(TEST_ENCODING_SIZE, bigan.encoding_size)
        self.assertEqual([(None, TEST_ENCODING_SIZE), (None, TEST_ENCODING_SIZE)], bigan._generator.get_input_shape_at(0))
        self.assertEqual((None, TEST_GENE_COUNT), bigan._generator.output_shape)

    def test_trainings_run(self):
        test_data, test_losses = ['some', 'data'], (0.7, 0.8, 0.8)
        self.trainer.sample_cell_data = sample_mock = MagicMock(return_value=test_data)
        self.trainer.network.trainings_step = trainings_step_mock = MagicMock(return_value=test_losses)

        test_iterations = 6
        test_batch_iterations = test_iterations * TEST_BATCHES_PER_ITERATION
        self.trainer.run(test_iterations, None)
        self.assertEqual(sample_mock.call_count, test_batch_iterations)
        trainings_step_mock.assert_called_with(test_data)
        self.assertEqual(trainings_step_mock.call_count, test_batch_iterations)

    def test_training_runs_interceptor(self):
        intercept_mock = MagicMock()
        self.trainer.network.trainings_step = MagicMock(return_value=(1, 2, 3))
        self.trainer.run(3, intercept_mock)

        intercept_mock.assert_called_with(2, (4, 8, 12))
