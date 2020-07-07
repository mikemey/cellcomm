import os

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import Model, layers, optimizers, losses

CELL_MATRIX_FILE = os.path.join(os.path.dirname(__file__),
                                '..', 'data', 'GSE122930_Sham_1_week_matrix.mtx')


def load_matrix(file):
    df = pd.read_csv(file, header=None, skiprows=3,
                     delim_whitespace=True, names=['gene', 'barcode', 'p'])
    return df.pivot_table(index='barcode', columns='gene', values='p', fill_value=0)


def _build_generator(encoding_size, gene_size):
    encoding_in = layers.Input(shape=encoding_size)
    x = layers.Dense(encoding_size * 10, activation=tf.nn.relu)(encoding_in)
    cell_out = layers.Dense(gene_size, activation=tf.nn.relu)(x)
    return Model(encoding_in, cell_out, name='cell_generator')


def _build_encoder(encoding_size, gene_size):
    cell_in = layers.Input(shape=gene_size)
    x = layers.Dense(encoding_size * 10, activation=tf.nn.relu)(cell_in)
    encoding_out = layers.Dense(encoding_size, activation=tf.nn.sigmoid)(x)
    return Model(cell_in, encoding_out, name='cell_encoder')


def _build_discriminator(encoding_size, gene_size):
    encoding_in = layers.Input(shape=encoding_size, name='encoding_input')
    cell_in = layers.Input(shape=gene_size, name='cell_input')

    x = layers.Concatenate()([encoding_in, cell_in])
    prob = layers.Dense(1, activation=tf.nn.sigmoid)(x)
    return Model([encoding_in, cell_in], prob, name='source_discriminator')


class CellBiGan:
    TRAIN_GENERATOR = (True, False, False)
    TRAIN_ENCODER = (False, True, False)
    TRAIN_DISCRIMINATOR = (False, False, True)

    def __init__(self, encoding_size, gene_size,
                 discr_optimizer=optimizers.Adam(),
                 discr_loss=losses.binary_crossentropy,
                 gen_optimizer=optimizers.Adam(),
                 gen_loss=losses.mse,
                 enc_optimizer=optimizers.Adam(),
                 enc_loss=losses.mse):
        self.encoding_size = encoding_size
        self._generator = _build_generator(encoding_size, gene_size)
        self._encoder = _build_encoder(encoding_size, gene_size)
        self._discriminator = _build_discriminator(encoding_size, gene_size)
        self._discriminator.compile(optimizer=discr_optimizer, loss=discr_loss)

        gen_output = self._discriminator((self._generator.input, self._generator.output))
        self._generator_train_model = Model(self._generator.inputs, gen_output, name='generator-trainings-model')
        self._generator_train_model.compile(optimizer=gen_optimizer, loss=gen_loss)

        enc_output = self._discriminator((self._encoder.output, self._encoder.input))
        self._encoder_train_model = Model(self._encoder.inputs, enc_output, name='encoder-trainings-model')
        self._encoder_train_model.compile(optimizer=enc_optimizer, loss=enc_loss)

    def summary(self):
        self._generator.summary()
        self._encoder.summary()
        self._discriminator.summary()

    def _random_encoding_vector(self, v_count):
        return tf.random.uniform(shape=(v_count, self.encoding_size), minval=0, maxval=1)

    def _set_trainings_mode(self, mode):
        self._generator.trainable, self._encoder.trainable, self._discriminator.trainable = mode

    def trainings_step(self, sampled_batch):
        z = self._random_encoding_vector(len(sampled_batch))
        y_ones = tf.ones(len(sampled_batch))
        y_zeros = tf.zeros(len(sampled_batch))

        g_loss = self.__train_generator(z, y_ones)
        e_loss = self.__train_encoder(sampled_batch, y_zeros)

        d_loss_1 = self.__train_discriminator(z, self._generator.predict(z), y_zeros)
        d_loss_2 = self.__train_discriminator(self._encoder.predict(sampled_batch), sampled_batch, y_ones)
        d_loss = np.mean([d_loss_1, d_loss_2])
        return g_loss, e_loss, d_loss

    def __train_generator(self, encoding, target):
        self._set_trainings_mode(self.TRAIN_GENERATOR)
        return self._generator_train_model.train_on_batch(encoding, target)

    def __train_encoder(self, cell_data, target):
        self._set_trainings_mode(self.TRAIN_ENCODER)
        return self._encoder_train_model.train_on_batch(cell_data, target)

    def __train_discriminator(self, encoding, cell_data, target):
        self._set_trainings_mode(self.TRAIN_DISCRIMINATOR)
        return self._discriminator.train_on_batch((encoding, cell_data), target)


class CellTraining:
    def __init__(self, matrix_file=CELL_MATRIX_FILE, batch_size=64):
        self.batch_size = batch_size
        self.data = load_matrix(matrix_file)

    def _sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)
