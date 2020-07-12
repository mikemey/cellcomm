import os
from unittest.mock import MagicMock, call

import numpy as np
import tensorflow as tf
from pandas import DataFrame

from bigan_classify import ClassifyCellBiGan
from bigan_cont import ContinuousCellBiGan
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


class ClassifyBiGanTestCase(TFTestCase):
    def test_generator_model(self):
        generator = ClassifyCellBiGan(encoding_size=15, gene_size=1000)._generator
        self.assertTrue(generator._is_compiled)
        self.assertEqual((None, 15), generator.input_shape)
        self.assertEqual((None, 1000), generator.output_shape)
        self.assertEqual(tf.nn.relu, generator.layers[-1].activation)

    def test_encoder_model(self):
        encoder = ClassifyCellBiGan(encoding_size=12, gene_size=100)._encoder
        self.assertTrue(encoder._is_compiled)
        self.assertEqual((None, 100), encoder.input_shape)
        self.assertEqual((None, 12), encoder.output_shape)
        self.assertEqual(tf.nn.softmax, encoder.layers[-1].activation)

    def test_discriminator_model(self):
        discriminator = ClassifyCellBiGan(encoding_size=4, gene_size=5)._discriminator
        self.assertTrue(discriminator._is_compiled)
        self.assertEqual([(None, 4), (None, 5)], discriminator.get_input_shape_at(0))
        self.assertEqual((None, 1), discriminator.get_output_shape_at(0))
        self.assertEqual(tf.nn.sigmoid, discriminator.layers[-1].activation)

    def test_create_encoding_vector_classification(self):
        np.random.seed(21)
        cell_bigan = ClassifyCellBiGan(encoding_size=4, gene_size=1)
        hv = cell_bigan._get_encoding_vector(5)
        exp = np.array([[0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]])
        self.assertDeepEqual(exp, hv)

    def test_bigan_models(self):
        bigan = ClassifyCellBiGan(encoding_size=4, gene_size=6)
        gen_train_model = bigan._generator_train_model
        self.assertTrue(gen_train_model._is_compiled)
        self.assertEqual((None, 4), gen_train_model.input_shape)
        self.assertEqual((None, 1), gen_train_model.output_shape)

        enc_train_model = bigan._encoder_train_model
        self.assertTrue(enc_train_model._is_compiled)
        self.assertEqual((None, 6), enc_train_model.input_shape)
        self.assertEqual((None, 1), enc_train_model.output_shape)

    def test_training_modes(self):
        bigan = ClassifyCellBiGan(encoding_size=4, gene_size=6)

        def assert_trainings_mode(gen, enc, discr):
            self.assertEqual(bigan._generator.trainable, gen)
            self.assertEqual(bigan._encoder.trainable, enc)
            self.assertEqual(bigan._discriminator.trainable, discr)

        bigan._set_trainings_mode(ClassifyCellBiGan.TRAIN_GENERATOR)
        assert_trainings_mode(True, False, False)

        bigan._set_trainings_mode(ClassifyCellBiGan.TRAIN_ENCODER)
        assert_trainings_mode(False, True, False)

        bigan._set_trainings_mode(ClassifyCellBiGan.TRAIN_DISCRIMINATOR)
        assert_trainings_mode(False, False, True)

    def test_training_step(self):
        rnd_encodings = tf.constant([[0.123] * TEST_BATCH_SIZE])
        sampled_batch = DataFrame([[14, 15]] * TEST_BATCH_SIZE)

        bigan = ClassifyCellBiGan(encoding_size=1, gene_size=2)
        bigan._set_trainings_mode = trainings_mode_mock = MagicMock()
        bigan._get_encoding_vector = get_encoding_mock = MagicMock(return_value=rnd_encodings)
        bigan._generator_train_model.train_on_batch = gen_train_mock = MagicMock(return_value='g-loss')
        bigan._encoder_train_model.train_on_batch = enc_train_mock = MagicMock(return_value='e-loss')

        gen_prediction = tf.constant([[10, 11]] * TEST_BATCH_SIZE)
        enc_prediction = tf.constant([[2]] * TEST_BATCH_SIZE)
        bigan.generate_cells = gen_cells_mock = MagicMock(return_value=gen_prediction)
        bigan.encode_genes = enc_genes_mock = MagicMock(return_value=enc_prediction)
        bigan._discriminator.train_on_batch = discr_train_mock = MagicMock(side_effect=[3, 5])

        losses = bigan.trainings_step(sampled_batch)
        self.assertEqual(('g-loss', 'e-loss', 4), losses)

        trainings_mode_mock.assert_has_calls([
            call(ClassifyCellBiGan.TRAIN_GENERATOR),
            call(ClassifyCellBiGan.TRAIN_ENCODER),
            call(ClassifyCellBiGan.TRAIN_DISCRIMINATOR)]
        )
        self.assertEqual(2, get_encoding_mock.call_count)
        get_encoding_mock.assert_called_with(TEST_BATCH_SIZE)

        def assert_mock_calls(mock, args):
            for ix, m_arg in enumerate(args):
                self.assertDeepEqual(m_arg, mock.call_args[0][ix])

        y_gen, y_enc = tf.repeat(0.9, TEST_BATCH_SIZE), tf.repeat(0.1, TEST_BATCH_SIZE)
        assert_mock_calls(gen_train_mock, args=(rnd_encodings, y_gen))
        assert_mock_calls(enc_train_mock, args=(sampled_batch, y_enc))
        assert_mock_calls(gen_cells_mock, args=(rnd_encodings,))
        assert_mock_calls(enc_genes_mock, args=(sampled_batch,))

        self.assertDeepEqual(rnd_encodings, discr_train_mock.call_args_list[0][0][0][0])
        self.assertDeepEqual(gen_prediction, discr_train_mock.call_args_list[0][0][0][1])
        self.assertDeepEqual(y_enc, discr_train_mock.call_args_list[0][0][1])

        self.assertDeepEqual(enc_prediction, discr_train_mock.call_args_list[1][0][0][0])
        self.assertDeepEqual(sampled_batch, discr_train_mock.call_args_list[1][0][0][1])
        self.assertDeepEqual(y_gen, discr_train_mock.call_args_list[1][0][1])

    def test_encode_genes(self):
        bigan = ClassifyCellBiGan(encoding_size=2, gene_size=4)
        test_genes = [[5, 3, 1, 4], [1, 5, 13, 7]]
        test_prediction = [[0.1, 0.3], [0.7, 0.3], [0.001, 0.99]]
        test_hot_enc = [[0, 1], [1, 0], [0, 1]]
        bigan._encoder.predict = predict_mock = MagicMock(return_value=test_prediction)

        self.assertDeepEqual(test_hot_enc, bigan.encode_genes(test_genes))
        predict_mock.assert_called_with(test_genes)

    def test_generate_data(self):
        random_input = [[1, 0], [0, 1]]
        test_prediction = [[0.3, 12.59939265, 2.4894546, 0.01],
                           [0.9, 4.7007282, 0, 2.07244989]]
        expected_cells = [[0, 13, 2, 0], [1, 5, 0, 2]]
        bigan = ClassifyCellBiGan(encoding_size=2, gene_size=4)
        bigan._generator.predict = predict_mock = MagicMock(return_value=test_prediction)

        gen_cells = bigan.generate_cells(random_input)
        self.assertDeepEqual(expected_cells, gen_cells)
        predict_mock.assert_called_with(random_input)


class ContinuousBiGanTestCase(TFTestCase):
    def test_encoder_model(self):
        encoder = ContinuousCellBiGan(encoding_size=12, gene_size=100)._encoder
        self.assertTrue(encoder._is_compiled)
        self.assertEqual((None, 100), encoder.input_shape)
        self.assertEqual((None, 12), encoder.output_shape)
        self.assertEqual(tf.nn.sigmoid, encoder.layers[-1].activation)

    def test_create_encoding_vector_random(self):
        cell_bigan = ContinuousCellBiGan(encoding_size=20, gene_size=1)
        for _ in range(30):
            cell_encoding = cell_bigan._get_encoding_vector(3)
            self.assertEqual((3, 20), cell_encoding.shape)
            self.assertTrue(np.all(cell_encoding > 0), f'cell_encoding with values < 0:\n{cell_encoding}')
            self.assertTrue(np.all(cell_encoding < 1), f'cell_encoding with values > 1:\n{cell_encoding}')

    def test_encode_genes(self):
        bigan = ContinuousCellBiGan(encoding_size=2, gene_size=4)
        test_genes = [[5, 3, 1, 4], [1, 5, 13, 7]]
        test_prediction = [[0.1, 0.3], [0.7, 0.3], [0.001, 0.99]]
        bigan._encoder.predict = predict_mock = MagicMock(return_value=test_prediction)

        self.assertDeepEqual(test_prediction, bigan.encode_genes(test_genes))
        predict_mock.assert_called_with(test_genes)
