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


def _build_generator(encoding_shape, gene_count):
    encoding_in = layers.Input(encoding_shape)
    x = layers.Dense(encoding_shape[0] * 10, activation=tf.nn.relu)(encoding_in)
    data_out = layers.Dense(gene_count, activation=tf.nn.relu)(x)
    return Model(encoding_in, data_out, name='Cell generator')


class CellBigan:
    def __init__(self, encoding_shape, gene_count):
        self._generator = _build_generator(encoding_shape, gene_count)
        self.summary()

    def summary(self):
        self._generator.summary()


class CellTraining:
    def __init__(self, matrix_file=CELL_MATRIX_FILE, batch_size=32):
        self.batch_size = batch_size
        self.data = load_matrix(matrix_file)

    def sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)
