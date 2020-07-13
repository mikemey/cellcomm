from abc import abstractmethod
from typing import final

import tensorflow as tf


class BasicBiGan:
    TRAIN_GENERATOR = (True, False, False)
    TRAIN_ENCODER = (False, True, False)
    TRAIN_DISCRIMINATOR = (False, False, True)

    def __init__(self, encoding_size, gene_size,
                 generator_factory, encoder_factory, discriminator_factory):
        self.encoding_size = encoding_size
        self._generator = generator_factory(encoding_size, gene_size)
        self._encoder = encoder_factory(encoding_size, gene_size)
        self._discriminator = discriminator_factory(encoding_size, gene_size)

    @final
    def summary(self):
        self._generator.summary()
        self._encoder.summary()
        self._discriminator.summary()

    @final
    def encoding_prediction(self, cell_data):
        return self._encoder.predict(cell_data)

    @final
    def cell_prediction(self, gen_input):
        prediction = self._generator.predict(gen_input)
        return tf.math.round(prediction)

    @final
    def _set_trainings_mode(self, mode):
        self._generator.trainable, self._encoder.trainable, self._discriminator.trainable = mode

    @abstractmethod
    def trainings_step(self, sampled_batch):
        pass
