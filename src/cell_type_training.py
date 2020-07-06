import os

import pandas as pd
import tensorflow as tf
from tensorflow.keras import Model, layers

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
    return Model(encoding_in, cell_out, name='Cell generator')


def _build_encoder(encoding_size, gene_size):
    cell_in = layers.Input(shape=gene_size)
    x = layers.Dense(encoding_size * 10, activation=tf.nn.relu)(cell_in)
    encoding_out = layers.Dense(encoding_size, activation=tf.nn.sigmoid)(x)
    return Model(cell_in, encoding_out, name='Cell encoder')


def _build_discriminator(encoding_size, gene_size):
    inputs = layers.Input(shape=(encoding_size, gene_size))
    x = layers.Dense(encoding_size + gene_size, activation=tf.nn.relu)(inputs)
    x = layers.Flatten()(x)
    prob = layers.Dense(1, activation=tf.nn.sigmoid)(x)
    return Model(inputs, prob, name='Cell discriminator')


class CellBiGan:
    def __init__(self, encoding_size, gene_size):
        self.encoding_size = encoding_size
        self._generator = _build_generator(encoding_size, gene_size)
        self._encoder = _build_encoder(encoding_size, gene_size)
        self._discriminator = _build_discriminator(encoding_size, gene_size)

    def summary(self):
        self._generator.summary()
        self._encoder.summary()
        self._discriminator.summary()

    def _random_encoding_vector(self):
        return tf.random.uniform(shape=(self.encoding_size,), minval=0, maxval=1)


class CellTraining:
    def __init__(self, matrix_file=CELL_MATRIX_FILE, batch_size=32):
        self.batch_size = batch_size
        self.data = load_matrix(matrix_file)

    def sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)
