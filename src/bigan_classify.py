from typing import Callable

import numpy as np
import tensorflow as tf
from tensorflow.keras import Model, layers, optimizers, losses, utils

from bigan_basic import BasicBiGan


def _build_generator(encoding_size, gene_size):
    encoding_in = layers.Input(shape=encoding_size)
    x = layers.Dense(50, activation=tf.nn.sigmoid)(encoding_in)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    # x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, encoding_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    # x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(1024, activation=tf.nn.sigmoid)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, encoding_in])
    cell_out = layers.Dense(gene_size, activation=tf.nn.relu)(x)
    return Model(encoding_in, cell_out, name='cell_generator')


def _build_encoder(encoding_size, gene_size):
    cell_in = layers.Input(shape=gene_size)
    # normal_cell_in = layers.BatchNormalization()(cell_in)
    proc_cell_in = layers.Dense(1000, activation=tf.nn.sigmoid)(cell_in)
    # x = layers.Dropout(0.15)(proc_cell_in)
    # x = layers.Concatenate()([x, proc_cell_in])
    x = layers.Dropout(0.15)(proc_cell_in)
    x = layers.Dense(300, activation=tf.nn.sigmoid)(x)
    x = layers.Dropout(0.15)(x)
    x = layers.Concatenate()([x, proc_cell_in])
    x = layers.Dense(150, activation=tf.nn.sigmoid)(x)
    encoding_out = layers.Dense(encoding_size, activation=tf.nn.softmax)(x)
    return Model(cell_in, encoding_out, name='cell_encoder')


def _build_discriminator(encoding_size, gene_size):
    encoding_in = layers.Input(shape=encoding_size, name='encoding_input')
    cell_in = layers.Input(shape=gene_size, name='cell_input')

    x = layers.Dense(50, activation=tf.nn.sigmoid)(encoding_in)
    x2 = layers.Dense(50, activation=tf.nn.sigmoid)(encoding_in)
    x = layers.Concatenate()([x, x2, encoding_in])
    x = layers.Dropout(0.15)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    summary_enc = layers.Dense(256, activation=tf.nn.sigmoid)(x)

    l_widths = [int(gene_size * f) for f in [0.25, 0.1]]
    x = layers.Dense(l_widths[0], activation=tf.nn.sigmoid)(cell_in)
    x = layers.Dropout(0.15)(x)
    x = layers.Concatenate()([x, cell_in])
    x = layers.Dense(l_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.15)(x)
    x = layers.Concatenate()([x, cell_in])
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    summary_gene = layers.Dense(300, activation=tf.nn.sigmoid)(x)

    combined_summaries = layers.Concatenate()([summary_enc, summary_gene])
    combined_in = layers.Concatenate()([encoding_in, cell_in])
    x = layers.Concatenate()([combined_summaries, combined_in])
    x = layers.Dense(l_widths[0], activation=tf.nn.sigmoid)(x)
    x = layers.Dropout(0.15)(x)
    x = layers.Concatenate()([x, combined_summaries])
    x = layers.Dense(l_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.15)(x)
    x = layers.Dense(50, activation=tf.nn.sigmoid)(x)
    x = layers.Dense(50, activation=tf.nn.sigmoid)(x)
    x = layers.Dense(10, activation=tf.nn.sigmoid)(x)
    prob = layers.Dense(1, activation=tf.nn.sigmoid)(x)
    return Model([encoding_in, cell_in], prob, name='cell_discriminator')


def print_dot():
    print('.', end='', flush=True)


class ClassifyCellBiGan(BasicBiGan):
    def __init__(self, encoding_size, gene_size,
                 generator_factory: Callable[[int, int], Model] = _build_generator,
                 encoder_factory: Callable[[int, int], Model] = _build_encoder,
                 discriminator_factory: Callable[[int, int], Model] = _build_discriminator):
        super().__init__(encoding_size, gene_size, generator_factory, encoder_factory, discriminator_factory)
        discr_optimizer = optimizers.Adam()
        discr_loss = losses.binary_crossentropy

        self._discriminator.trainable = False
        gen_output = self._discriminator((self._generator.input, self._generator.output))
        self._generator_train_model = Model(self._generator.inputs, gen_output, name='generator-trainings-model')
        self._generator_train_model.compile(optimizer=discr_optimizer, loss=discr_loss)

        self._discriminator.trainable = False
        enc_output = self._discriminator((self._encoder.output, self._encoder.input))
        self._encoder_train_model = Model(self._encoder.inputs, enc_output, name='encoder-trainings-model')
        self._encoder_train_model.compile(optimizer=discr_optimizer, loss=discr_loss)

        self._discriminator.trainable = True
        self._discriminator.compile(optimizer=discr_optimizer, loss=discr_loss)

    def _get_encoding_vector(self, batch_size):
        rand_ixs = np.random.randint(0, self.encoding_size, batch_size)
        return tf.keras.utils.to_categorical(rand_ixs, self.encoding_size)

    def trainings_encoding_prediction(self, cell_data):
        prediction = self.encoding_prediction(cell_data)
        argmax = tf.math.argmax(prediction, -1)
        return utils.to_categorical(argmax, num_classes=self.encoding_size)

    def trainings_step(self, sampled_batch):
        batch_size = len(sampled_batch)
        y_ones = tf.repeat(0.95, batch_size)
        y_zeros = tf.zeros(batch_size)

        z = self._get_encoding_vector(batch_size)
        print_dot()
        g_loss = self.__train_generator(z, y_ones)
        print_dot()
        e_loss = self.__train_encoder(sampled_batch, y_zeros)

        z = self._get_encoding_vector(batch_size)
        print_dot()
        d_loss_1 = self.__train_discriminator(z, self.cell_prediction(z), y_zeros)
        print_dot()
        d_loss_2 = self.__train_discriminator(self.trainings_encoding_prediction(sampled_batch), sampled_batch, y_ones)
        d_loss = np.mean([d_loss_1, d_loss_2])

        return g_loss, e_loss, d_loss

    def __train_generator(self, encoding, target):
        return self._generator_train_model.train_on_batch(encoding, target)

    def __train_encoder(self, cell_data, target):
        return self._encoder_train_model.train_on_batch(cell_data, target)

    def __train_discriminator(self, encoding, cell_data, target):
        return self._discriminator.train_on_batch((encoding, cell_data), target)
