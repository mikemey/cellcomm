import os
from unittest.mock import MagicMock, call

import numpy as np
import tensorflow as tf
from pandas import DataFrame

from cell_bigan import CellBiGan
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


class CellBiGanTestCase(TFTestCase):
    def test_generator_model(self):
        generator = CellBiGan(encoding_size=15, gene_size=1000)._generator
        self.assertEqual((None, 15), generator.input_shape)
        self.assertEqual((None, 1000), generator.output_shape)
        self.assertEqual(tf.nn.relu, generator.layers[-1].activation)

    def test_encoder_model(self):
        encoder = CellBiGan(encoding_size=12, gene_size=100)._encoder
        self.assertEqual((None, 100), encoder.input_shape)
        self.assertEqual((None, 12), encoder.output_shape)
        self.assertEqual(tf.nn.sigmoid, encoder.layers[-1].activation)

    def test_discriminator_model(self):
        discriminator = CellBiGan(encoding_size=4, gene_size=5)._discriminator
        self.assertTrue(discriminator._is_compiled)
        self.assertEqual([(None, 4), (None, 5)], discriminator.get_input_shape_at(0))
        self.assertEqual((None, 1), discriminator.get_output_shape_at(0))
        self.assertEqual(tf.nn.sigmoid, discriminator.layers[-1].activation)

    def test_create_random_encoding_vector(self):
        cell_bigan = CellBiGan(encoding_size=20, gene_size=1)
        for _ in range(100):
            cell_encoding = cell_bigan._random_encoding_vector(3)
            self.assertEqual((3, 20), cell_encoding.shape)
            self.assertTrue(np.all(cell_encoding > 0), f'cell_encoding with values < 0:\n{cell_encoding}')
            self.assertTrue(np.all(cell_encoding < 1), f'cell_encoding with values > 1:\n{cell_encoding}')

    def test_bigan_models(self):
        bigan = CellBiGan(encoding_size=4, gene_size=6)
        gen_train_model = bigan._generator_train_model
        self.assertTrue(gen_train_model._is_compiled)
        self.assertEqual((None, 4), gen_train_model.input_shape)
        self.assertEqual((None, 1), gen_train_model.output_shape)

        enc_train_model = bigan._encoder_train_model
        self.assertTrue(enc_train_model._is_compiled)
        self.assertEqual((None, 6), enc_train_model.input_shape)
        self.assertEqual((None, 1), enc_train_model.output_shape)

    def test_training_modes(self):
        bigan = CellBiGan(encoding_size=4, gene_size=6)

        def assert_trainings_mode(gen, enc, discr):
            self.assertEqual(bigan._generator.trainable, gen)
            self.assertEqual(bigan._encoder.trainable, enc)
            self.assertEqual(bigan._discriminator.trainable, discr)

        bigan._set_trainings_mode(CellBiGan.TRAIN_GENERATOR)
        assert_trainings_mode(True, False, False)

        bigan._set_trainings_mode(CellBiGan.TRAIN_ENCODER)
        assert_trainings_mode(False, True, False)

        bigan._set_trainings_mode(CellBiGan.TRAIN_DISCRIMINATOR)
        assert_trainings_mode(False, False, True)

    def test_training_step(self):
        rnd_encodings = tf.constant([[0.123] * TEST_BATCH_SIZE])
        sampled_batch = DataFrame([[14, 15]] * TEST_BATCH_SIZE)

        bigan = CellBiGan(encoding_size=1, gene_size=2)
        bigan._set_trainings_mode = trainings_mode_mock = MagicMock()
        bigan._random_encoding_vector = random_enc_mock = MagicMock(return_value=rnd_encodings)
        bigan._generator_train_model.train_on_batch = gen_train_mock = MagicMock(return_value='g-loss')
        bigan._encoder_train_model.train_on_batch = enc_train_mock = MagicMock(return_value='e-loss')

        gen_prediction = tf.constant([[10, 11]] * TEST_BATCH_SIZE)
        enc_prediction = tf.constant([[2]] * TEST_BATCH_SIZE)
        bigan._generator.predict = gen_predict_mock = MagicMock(return_value=gen_prediction)
        bigan._encoder.predict = enc_predict_mock = MagicMock(return_value=enc_prediction)
        bigan._discriminator.train_on_batch = discr_train_mock = MagicMock(side_effect=[3, 5])

        losses = bigan.trainings_step(sampled_batch)
        self.assertEqual(('g-loss', 'e-loss', 4), losses)

        trainings_mode_mock.assert_has_calls([
            call(CellBiGan.TRAIN_GENERATOR),
            call(CellBiGan.TRAIN_ENCODER),
            call(CellBiGan.TRAIN_DISCRIMINATOR)]
        )
        random_enc_mock.assert_called_once_with(TEST_BATCH_SIZE)

        def assert_mock_calls(mock, args):
            for ix, m_arg in enumerate(args):
                self.assertDeepEqual(m_arg, mock.call_args[0][ix])

        y_gen, y_enc = tf.repeat(0.9, TEST_BATCH_SIZE), tf.repeat(0.1, TEST_BATCH_SIZE)
        assert_mock_calls(gen_train_mock, args=(rnd_encodings, y_gen))
        assert_mock_calls(enc_train_mock, args=(sampled_batch, y_enc))
        assert_mock_calls(gen_predict_mock, args=(rnd_encodings,))
        assert_mock_calls(enc_predict_mock, args=(sampled_batch,))

        self.assertDeepEqual(rnd_encodings, discr_train_mock.call_args_list[0][0][0][0])
        self.assertDeepEqual(gen_prediction, discr_train_mock.call_args_list[0][0][0][1])
        self.assertDeepEqual(y_enc, discr_train_mock.call_args_list[0][0][1])

        self.assertDeepEqual(enc_prediction, discr_train_mock.call_args_list[1][0][0][0])
        self.assertDeepEqual(sampled_batch, discr_train_mock.call_args_list[1][0][0][1])
        self.assertDeepEqual(y_gen, discr_train_mock.call_args_list[1][0][1])

    def test_predict_encoding(self):
        bigan = CellBiGan(encoding_size=1, gene_size=1)
        test_input, test_return = 'input', 'return'
        bigan._encoder.predict = predict_mock = MagicMock(return_value=test_return)

        self.assertEqual(test_return, bigan.predict_encoding(test_input))
        predict_mock.assert_called_with(test_input)
