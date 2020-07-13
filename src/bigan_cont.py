import tensorflow as tf
from tensorflow.keras import Model, layers

from bigan_classify import ClassifyCellBiGan


def _build_generator(encoding_size, gene_size):
    layer_widths = [int(gene_size * f) for f in [0.25, 0.1]]

    encoding_in = layers.Input(shape=encoding_size)
    x = layers.Dense(50, activation=tf.nn.sigmoid)(encoding_in)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(layer_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.Dense(layer_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dense(layer_widths[0], activation=tf.nn.relu)(x)
    cell_out = layers.Dense(gene_size, activation=tf.nn.relu)(x)
    return Model(encoding_in, cell_out, name='cell_generator')


def _build_encoder(encoding_size, gene_size):
    layer_widths = [int(gene_size * f) for f in [0.25, 0.1]]

    cell_in = layers.Input(shape=gene_size)
    x = layers.Dense(layer_widths[0], activation=tf.nn.sigmoid)(cell_in)
    x = layers.Dropout(0.15)(x)
    x = layers.Dense(layer_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.Concatenate()([x, cell_in])
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(layer_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.Dense(50, activation=tf.nn.sigmoid)(x)
    x = layers.Dense(50, activation=tf.nn.sigmoid)(x)
    encoding_out = layers.Dense(encoding_size, activation=tf.nn.sigmoid)(x)
    return Model(cell_in, encoding_out, name='cell_encoder')


class ContinuousCellBiGan(ClassifyCellBiGan):
    def __init__(self, encoding_size, gene_size):
        super().__init__(
            encoding_size, gene_size,
            generator_factory=_build_generator,
            encoder_factory=_build_encoder
        )

    def _get_encoding_vector(self, batch_size):
        return tf.random.uniform(shape=(batch_size, self.encoding_size), minval=0, maxval=1)

    def trainings_encoding_prediction(self, cell_data):
        return self.encoding_prediction(cell_data)
