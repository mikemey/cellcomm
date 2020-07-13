import os
from unittest.mock import MagicMock

from bigan_basic import BasicBiGan
from tf_testcase import TFTestCase

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'


class BasicBiGanTestCase(TFTestCase):
    def setUp(self):
        self.gen_mock, self.enc_mock, self.discr_mock = MagicMock(), MagicMock(), MagicMock()
        self.bigan = BasicBiGan(
            encoding_size=15, gene_size=1000,
            generator_factory=MagicMock(return_value=self.gen_mock),
            encoder_factory=MagicMock(return_value=self.enc_mock),
            discriminator_factory=MagicMock(return_value=self.discr_mock)
        )

    def test_create_components(self):
        self.assertEqual(self.enc_mock, self.bigan._encoder)
        self.assertEqual(self.gen_mock, self.bigan._generator)
        self.assertEqual(self.discr_mock, self.bigan._discriminator)

    def test_encoding_prediction(self):
        test_genes = [[5, 3, 1, 4], [1, 5, 13, 7]]
        test_prediction = [[0.1, 0.3], [0.7, 0.3], [0.001, 0.99]]
        self.bigan._encoder.predict = predict_mock = MagicMock(return_value=test_prediction)

        self.assertDeepEqual(test_prediction, self.bigan.encoding_prediction(test_genes))
        predict_mock.assert_called_with(test_genes)

    def test_cell_data_prediction(self):
        random_input = [[1, 0], [0, 1]]
        test_prediction = [[0.3, 12.59939265, 2.4894546, 0.01],
                           [0.9, 4.7007282, 0, 2.07244989]]
        expected_cells = [[0, 13, 2, 0], [1, 5, 0, 2]]
        self.bigan._generator.predict = predict_mock = MagicMock(return_value=test_prediction)

        gen_cells = self.bigan.cell_prediction(random_input)
        self.assertDeepEqual(expected_cells, gen_cells)
        predict_mock.assert_called_with(random_input)
