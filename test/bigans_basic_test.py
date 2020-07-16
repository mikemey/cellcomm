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
        encoding_in = [[1, 0], [0, 1]]
        random_in = [[0.2, 0.], [0.99, 0.99]]
        test_prediction = [[0.3, 12.59939265, 2.4894546, 0.01],
                           [0.9, 4.7007282, 0, 2.07244989]]
        expected_cells = [[0, 13, 2, 0], [1, 5, 0, 2]]
        self.bigan._generator.predict = predict_mock = MagicMock(return_value=test_prediction)

        gen_cells = self.bigan.generate_cells(encoding_in, random_in)
        self.assertDeepEqual(expected_cells, gen_cells)
        predict_mock.assert_called_with((encoding_in, random_in))

    def test_random_uniform_vector(self):
        hv = self.bigan.random_uniform_vector(7)
        self.assertEqual((7, 15), hv.shape)

    def test_get_accuracy(self):
        data_batch = [[1, 2], [3, 4], [5, 6]]
        generated_cells = [6, 7, 8]
        random_encodings = [4, 5, 6]
        generated_encodings = [1, 2, 3]
        self.bigan.generate_cells = generator_mock = MagicMock(return_value=generated_cells)
        self.bigan.random_encoding_vector = random_encodings_mock = MagicMock(return_value=random_encodings)
        self.bigan.encoding_prediction = encoder_mock = MagicMock(return_value=generated_encodings)
        self.bigan._discriminator.predict = discr_mock = MagicMock(side_effect=[
            [0.1, 0.9, 0.55], [0.9, 0.9, 0.45]
        ])
        accuracies = self.bigan.evaluate_accuracy(data_batch)

        random_encodings_mock.assert_called_once_with(len(data_batch))
        generator_mock.assert_called_once_with(random_encodings)
        discr_mock.assert_any_call((random_encodings, generated_cells), use_multiprocessing=True)
        encoder_mock.assert_called_once_with(data_batch)
        discr_mock.assert_any_call((generated_encodings, data_batch), use_multiprocessing=True)
        self.assertEqual(((2, 1), (1, 2)), accuracies)
