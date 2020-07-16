import os
from unittest.mock import MagicMock

import numpy as np
import tensorflow as tf
from tensorflow.keras import optimizers, losses

from bigan_classify import ClassifyCellBiGan
from bigan_cont import ContinuousCellBiGan
from tf_testcase import TFTestCase

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'


class ClassifyBiGanTestCase(TFTestCase):
    def test_generator_train_model(self):
        bigan = ClassifyCellBiGan(encoding_size=15, gene_size=1000)
        generator = bigan._generator

        encoding_in = generator.layers[0]
        random_in = generator.layers[1]
        self.assertEqual('gen_encoding_in', encoding_in.name)
        self.assertEqual('gen_random_in', random_in.name)
        self.assertEqual([(None, 15)], encoding_in.input_shape)
        self.assertEqual([(None, 15)], random_in.input_shape)
        self.assertEqual((None, 1000), generator.output_shape)
        self.assertEqual(tf.nn.relu, generator.layers[-1].activation)

        gen_train = bigan._train_gen_w_discr
        self.assertTrue(gen_train._is_compiled)
        self.assertEqual(losses.binary_crossentropy, gen_train.loss)
        self.assertEqual(optimizers.RMSprop, type(gen_train.optimizer))
        self.assertEqual(tf.nn.sigmoid, gen_train.layers[-1].layers[-1].activation)

    def test_encoder_train_model(self):
        bigan = ClassifyCellBiGan(encoding_size=12, gene_size=100)
        encoder = bigan._encoder
        self.assertEqual((None, 100), encoder.input_shape)
        self.assertEqual((None, 12), encoder.output_shape)
        self.assertEqual(tf.nn.softmax, encoder.layers[-1].activation)

        enc_train = bigan._train_enc_w_discr
        self.assertTrue(enc_train._is_compiled)
        self.assertEqual(losses.binary_crossentropy, enc_train.loss)
        self.assertEqual(optimizers.RMSprop, type(enc_train.optimizer))
        self.assertEqual(tf.nn.sigmoid, enc_train.layers[-1].layers[-1].activation)

    def test_discriminator_model(self):
        discriminator = ClassifyCellBiGan(encoding_size=4, gene_size=5)._discriminator
        self.assertTrue(discriminator._is_compiled)
        self.assertEqual([(None, 4), (None, 5)], discriminator.get_input_shape_at(0))
        self.assertEqual((None, 1), discriminator.get_output_shape_at(0))
        self.assertEqual(losses.binary_crossentropy, discriminator.loss)
        self.assertEqual(optimizers.RMSprop, type(discriminator.optimizer))
        self.assertEqual(tf.nn.sigmoid, discriminator.layers[-1].activation)

    def test_random_encoding_vector(self):
        np.random.seed(21)
        cell_bigan = ClassifyCellBiGan(encoding_size=4, gene_size=1)
        hv = cell_bigan._random_encoding_vector(5)
        exp = np.array([[0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]])
        self.assertEqual((5, 4), np.shape(hv))
        self.assertDeepEqual(exp, hv)

    def test_training_models(self):
        bigan = ClassifyCellBiGan(encoding_size=4, gene_size=6)
        gen_train_model = bigan._train_gen_w_discr
        self.assertTrue(gen_train_model._is_compiled)
        self.assertEqual([(None, 4), (None, 4)], gen_train_model.input_shape)
        self.assertEqual((None, 1), gen_train_model.output_shape)

        enc_train_model = bigan._train_enc_w_discr
        self.assertTrue(enc_train_model._is_compiled)
        self.assertEqual((None, 6), enc_train_model.input_shape)
        self.assertEqual((None, 1), enc_train_model.output_shape)

    def test_trainings_encoding_prediction(self):
        bigan = ClassifyCellBiGan(encoding_size=2, gene_size=4)
        test_genes = [[5, 3, 1, 4], [1, 5, 13, 7]]
        test_prediction = [[0.1, 0.3], [0.7, 0.3], [0.001, 0.99]]
        test_hot_enc = [[0, 1], [1, 0], [0, 1]]
        bigan.encoding_prediction = predict_mock = MagicMock(return_value=test_prediction)

        self.assertDeepEqual(test_hot_enc, bigan.trainings_encoding_prediction(test_genes))
        predict_mock.assert_called_with(test_genes)


class ContinuousBiGanTestCase(TFTestCase):
    def test_generator_train_model(self):
        bigan = ContinuousCellBiGan(encoding_size=13, gene_size=100)
        generator = bigan._generator
        encoding_in = generator.layers[0]
        random_in = generator.layers[1]
        self.assertEqual('gen_encoding_in', encoding_in.name)
        self.assertEqual('gen_random_in', random_in.name)
        self.assertEqual([(None, 13)], encoding_in.input_shape)
        self.assertEqual([(None, 13)], random_in.input_shape)
        self.assertEqual((None, 100), generator.output_shape)
        self.assertEqual(tf.nn.relu, generator.layers[-1].activation)

        gen_train = bigan._train_gen_w_discr
        self.assertTrue(gen_train._is_compiled)
        self.assertEqual(losses.binary_crossentropy, gen_train.loss)
        self.assertEqual(optimizers.RMSprop, type(gen_train.optimizer))
        self.assertEqual(tf.nn.sigmoid, gen_train.layers[-1].layers[-1].activation)

    def test_encoder_model(self):
        encoder = ContinuousCellBiGan(encoding_size=12, gene_size=100)._encoder
        self.assertEqual(tf.nn.sigmoid, encoder.layers[-1].activation)

    def test_training_models(self):
        bigan = ContinuousCellBiGan(encoding_size=7, gene_size=11)
        gen_train_model = bigan._train_gen_w_discr
        self.assertTrue(gen_train_model._is_compiled)
        self.assertEqual([(None, 7), (None, 7)], gen_train_model.input_shape)
        self.assertEqual((None, 1), gen_train_model.output_shape)

        enc_train_model = bigan._train_enc_w_discr
        self.assertTrue(enc_train_model._is_compiled)
        self.assertEqual((None, 11), enc_train_model.input_shape)
        self.assertEqual((None, 1), enc_train_model.output_shape)

    def test_random_encoding_vector(self):
        cell_bigan = ContinuousCellBiGan(encoding_size=20, gene_size=1)
        for _ in range(30):
            cell_encoding = cell_bigan._random_encoding_vector(3)
            self.assertEqual((3, 20), cell_encoding.shape)
            self.assertTrue(np.all(cell_encoding > 0), f'cell_encoding with values < 0:\n{cell_encoding}')
            self.assertTrue(np.all(cell_encoding < 1), f'cell_encoding with values > 1:\n{cell_encoding}')

    def test_trainings_encoding_prediction(self):
        bigan = ContinuousCellBiGan(encoding_size=2, gene_size=4)
        test_genes = [[5, 3, 1, 4], [1, 5, 13, 7]]
        test_prediction = [[0.1, 0.3], [0.7, 0.3], [0.001, 0.99]]
        bigan._encoder.predict = predict_mock = MagicMock(return_value=test_prediction)

        self.assertDeepEqual(test_prediction, bigan.trainings_encoding_prediction(test_genes))
        predict_mock.assert_called_with(test_genes)
