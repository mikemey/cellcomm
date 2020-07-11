import numpy as np
import tensorflow as tf
from tensorflow.keras import Model, layers, optimizers, losses, utils


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

    combined_in = layers.Concatenate()([encoding_in, cell_in])
    skip = layers.Dense(700, activation=tf.nn.sigmoid)(combined_in)
    x = layers.Dropout(0.2)(skip)
    x = layers.Dense(300, activation=tf.nn.sigmoid)(x)
    x = layers.Concatenate()([x, skip])
    # x = layers.BatchNormalization()(x)
    x = layers.Dense(70, activation=tf.nn.sigmoid)(x)
    x = layers.Dropout(0.15)(x)
    x = layers.Dense(10, activation=tf.nn.sigmoid)(x)
    # x = layers.BatchNormalization()(x)
    prob = layers.Dense(1, activation=tf.nn.sigmoid)(x)
    return Model([encoding_in, cell_in], prob, name='cell_discriminator')


class ClassifyCellBiGan:
    TRAIN_GENERATOR = (True, False, False)
    TRAIN_ENCODER = (False, True, False)
    TRAIN_DISCRIMINATOR = (False, False, True)

    def __init__(self, encoding_size, gene_size,
                 gen_optimizer=optimizers.Adam(),
                 gen_loss=losses.mse,
                 enc_optimizer=optimizers.Adam(),
                 enc_loss=losses.categorical_crossentropy,
                 discr_optimizer=optimizers.Adam(),
                 discr_loss=losses.binary_crossentropy):
        self.encoding_size = encoding_size
        self._generator = _build_generator(encoding_size, gene_size)
        self._generator.compile(optimizer=gen_optimizer, loss=gen_loss)
        self._encoder = _build_encoder(encoding_size, gene_size)
        self._encoder.compile(optimizer=enc_optimizer, loss=enc_loss)

        self._discriminator = _build_discriminator(encoding_size, gene_size)
        self._discriminator.compile(optimizer=discr_optimizer, loss=discr_loss)

        gen_output = self._discriminator((self._generator.input, self._generator.output))
        self._generator_train_model = Model(self._generator.inputs, gen_output, name='generator-trainings-model')
        self._generator_train_model.compile(optimizer=discr_optimizer, loss=discr_loss)

        enc_output = self._discriminator((self._encoder.output, self._encoder.input))
        self._encoder_train_model = Model(self._encoder.inputs, enc_output, name='encoder-trainings-model')
        self._encoder_train_model.compile(optimizer=discr_optimizer, loss=discr_loss)

    def summary(self):
        self._generator.summary()
        self._encoder.summary()
        self._discriminator.summary()

    def _get_encoding_vector(self, batch_size):
        pass

    def print_some(self):
        print('\n------------UND I AH ==============================================')
    def _random_encoding_vector(self, batch_size):
        return tf.random.uniform(shape=(batch_size, self.encoding_size), minval=0, maxval=1)

    def _random_hot_encoding_vector(self, batch_size):
        rand_ixs = np.random.randint(0, self.encoding_size, batch_size)
        return tf.keras.utils.to_categorical(rand_ixs, self.encoding_size)

    def _set_trainings_mode(self, mode):
        self._generator.trainable, self._encoder.trainable, self._discriminator.trainable = mode

    def encode_genes(self, cell_data, to_hot_vector=True):
        prediction = self._encoder.predict(cell_data)
        if to_hot_vector:
            argmax = tf.math.argmax(prediction, -1)
            prediction = utils.to_categorical(argmax, num_classes=self.encoding_size)
        return prediction

    def generate_cells(self, z):
        prediction = self._generator.predict(z)
        return tf.math.round(prediction)

    def trainings_step(self, sampled_batch):
        batch_size = len(sampled_batch)
        z = self._random_hot_encoding_vector(batch_size)
        y_ones = tf.repeat(0.9, batch_size)
        y_zeros = tf.repeat(0.1, batch_size)

        g_loss = self.__train_generator(z, y_ones)
        e_loss = self.__train_encoder(sampled_batch, y_zeros)

        z = self._random_hot_encoding_vector(batch_size)
        d_loss_1 = self.__train_discriminator(z, self.generate_cells(z), y_zeros)
        d_loss_2 = self.__train_discriminator(self.encode_genes(sampled_batch), sampled_batch, y_ones)
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


class ContinuousCellBiGan(ClassifyCellBiGan):
    pass
