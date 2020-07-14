from typing import Callable

import numpy as np
import tensorflow as tf
from tensorflow.keras import Model, layers, optimizers, losses, utils

from bigan_basic import BasicBiGan


def _build_generator(encoding_size, gene_size):
    encoding_in = layers.Input(shape=encoding_size, name='gen_encoding_in')
    random_in = layers.Input(shape=encoding_size, name='gen_random_in')
    all_in = layers.Concatenate()([encoding_in, random_in])
    x = layers.Dense(50, activation=tf.nn.sigmoid)(all_in)
    x = layers.Concatenate()([x, all_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Concatenate()([x, all_in])
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(1024, activation=tf.nn.relu)(x)
    cell_out = layers.Dense(gene_size, activation=tf.nn.relu)(x)
    return Model([encoding_in, random_in], cell_out, name='cell_generator')


def _build_encoder(encoding_size, gene_size):
    cell_in = layers.Input(shape=gene_size, name='enc_cell_in')
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
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    summary_enc = layers.Dense(256, activation=tf.nn.sigmoid)(x)

    l_widths = [int(gene_size * f) for f in [0.3, 0.1, 0.05]]
    x = layers.Dense(l_widths[0], activation=tf.nn.sigmoid)(cell_in)
    x = layers.Dropout(0.15)(x)
    x = layers.Concatenate()([x, cell_in])
    x = layers.Dense(l_widths[1], activation=tf.nn.sigmoid)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.15)(x)
    x = layers.Dense(l_widths[2], activation=tf.nn.sigmoid)(x)
    x = layers.Dense(256, activation=tf.nn.sigmoid)(x)
    summary_gene = layers.Dense(256, activation=tf.nn.sigmoid)(x)

    combined_summaries = layers.Concatenate()([summary_enc, summary_gene])
    x = layers.Dense(300, activation=tf.nn.sigmoid)(combined_summaries)
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
        discr_optimizer = optimizers.RMSprop(learning_rate=0.0075, rho=0.85, momentum=0.1)

        self._generator.trainable = True
        self._encoder.trainable = False
        self._discriminator.trainable = False
        discr_gen_output = self._discriminator((self._generator.inputs[0], self._generator.output))
        self._train_gen_w_discr = Model(self._generator.inputs, discr_gen_output, name='train-generator-with-discriminator')
        self._train_gen_w_discr.compile(optimizer=discr_optimizer, loss=losses.binary_crossentropy)

        gen_output = self._generator((self._encoder.output, self._generator.inputs[1]))
        self._train_gen_w_enc = Model((self._encoder.inputs, self._generator.inputs[1]), gen_output, name='train-generator-with-encoder')
        self._train_gen_w_enc.compile(optimizer=discr_optimizer, loss=losses.mse)

        self._generator.trainable = False
        self._encoder.trainable = True
        self._discriminator.trainable = False
        discr_enc_output = self._discriminator((self._encoder.output, self._encoder.input))
        self._train_enc_w_discr = Model(self._encoder.inputs, discr_enc_output, name='train-encoder-with-discriminator')
        self._train_enc_w_discr.compile(optimizer=discr_optimizer, loss=losses.binary_crossentropy)

        enc_output = self._encoder(self._generator.output)
        self._train_enc_w_gen = Model(self._generator.inputs, enc_output, name='train-encoder-with-generator')
        self._train_enc_w_gen.compile(optimizer=discr_optimizer, loss=losses.mse)

        self._generator.trainable = False
        self._encoder.trainable = False
        self._discriminator.trainable = True
        self._discriminator.compile(optimizer=discr_optimizer, loss=losses.binary_crossentropy)

    def _random_encoding_vector(self, batch_size):
        rand_ixs = np.random.randint(0, self.encoding_size, batch_size)
        return tf.keras.utils.to_categorical(rand_ixs, self.encoding_size)

    def _random_uniform_vector(self, batch_size):
        return tf.random.uniform(shape=(batch_size, self.encoding_size), minval=0, maxval=1)

    def trainings_encoding_prediction(self, cell_data):
        prediction = self.encoding_prediction(cell_data)
        argmax = tf.math.argmax(prediction, -1)
        return utils.to_categorical(argmax, num_classes=self.encoding_size)

    def trainings_step(self, batch):
        batch_size = len(batch)
        y_ones = tf.repeat(0.95, batch_size)
        y_zeros = tf.zeros(batch_size)
        encodings = self._random_encoding_vector(batch_size)
        noise = self._random_uniform_vector(batch_size)

        g_loss = self.__train_generator(batch, encodings, noise, y_ones)
        e_loss = self.__train_encoder(batch, encodings, noise, y_zeros)

        generated_cells = self.generate_cells(encodings, noise)
        d_loss_1 = self.__train_discriminator(encodings, generated_cells, y_zeros)
        generated_encodings = self.trainings_encoding_prediction(batch)
        d_loss_2 = self.__train_discriminator(generated_encodings, batch, y_ones)
        d_loss = np.mean([d_loss_1, d_loss_2])

        return g_loss, e_loss, d_loss

    def __train_generator(self, cell_data, encodings, noise, y_ones):
        loss_from_discr = self._train_gen_w_discr.train_on_batch((encodings, noise), y_ones)
        loss_from_enc = self._train_gen_w_enc.train_on_batch((cell_data, noise), cell_data)
        return loss_from_discr + loss_from_enc

    def __train_encoder(self, cell_data, encodings, noise, y_zeros):
        loss_from_discr = self._train_enc_w_discr.train_on_batch(cell_data, y_zeros)
        loss_from_gen = self._train_enc_w_gen.train_on_batch((encodings, noise), encodings)
        return loss_from_discr + loss_from_gen

    def __train_discriminator(self, encodings, cell_data, target):
        return self._discriminator.train_on_batch((encodings, cell_data), target)
