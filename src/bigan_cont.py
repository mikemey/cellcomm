import tensorflow as tf
from tensorflow.keras import Model, layers, losses

from bigan_classify import ClassifyCellBiGan


def _build_generator(encoding_size, gene_size):
    encoding_in = layers.Input(shape=encoding_size)
    x = layers.Dense(50, activation=tf.nn.relu)(encoding_in)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.relu)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.relu)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(1024, activation=tf.nn.relu)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, encoding_in])
    cell_out = layers.Dense(gene_size, activation=tf.nn.relu)(x)
    return Model(encoding_in, cell_out, name='cell_generator')


def _build_encoder(encoding_size, gene_size):
    cell_in = layers.Input(shape=gene_size)
    normal_cell_in = layers.BatchNormalization()(cell_in)
    x = layers.Dropout(0.15)(normal_cell_in)
    x = layers.Dense(832, activation=tf.nn.relu)(x)
    x = layers.Concatenate()([x, normal_cell_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(300, activation=tf.nn.relu)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, normal_cell_in])
    encoding_out = layers.Dense(encoding_size, activation=tf.nn.sigmoid)(x)
    return Model(cell_in, encoding_out, name='cell_encoder')


class ContinuousCellBiGan(ClassifyCellBiGan):
    def __init__(self, encoding_size, gene_size):
        super(ContinuousCellBiGan, self).__init__(
            encoding_size, gene_size,
            generator_factory=_build_generator,
            gen_loss=losses.mse,
            encoder_factory=_build_encoder,
            enc_loss=losses.mse
        )

    def _get_encoding_vector(self, batch_size):
        return tf.random.uniform(shape=(batch_size, self.encoding_size), minval=0, maxval=1)
