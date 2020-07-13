from abc import abstractmethod
from typing import final, Callable

import numpy as np
import tensorflow as tf
from tensorflow.python.keras import Model


class BasicBiGan:
    def __init__(self, encoding_size, gene_size,
                 generator_factory: Callable[[int, int], Model],
                 encoder_factory: Callable[[int, int], Model],
                 discriminator_factory: Callable[[int, int], Model]
                 ):
        self.encoding_size = encoding_size
        self._generator = generator_factory(encoding_size, gene_size)
        self._encoder = encoder_factory(encoding_size, gene_size)
        self._discriminator = discriminator_factory(encoding_size, gene_size)
        self.all_components = self._generator, self._encoder, self._discriminator
        self.__prev_params = self.__last_layer_params()

    @final
    def summary(self):
        for component in self.all_components:
            component.summary()

    @final
    def encoding_prediction(self, cell_data):
        return self._encoder.predict(cell_data)

    @final
    def cell_prediction(self, gen_input):
        prediction = self._generator.predict(gen_input)
        return np.round(prediction)

    @abstractmethod
    def trainings_step(self, sampled_batch):
        pass

    def print_params_changes(self, msg):
        curr_params = self.__last_layer_params()
        changed = [components_changed(p_now, p_orig) for p_now, p_orig in zip(curr_params, self.__prev_params)]
        print(msg, 'G|E|D changed:', f'{changed[0]:1} | {changed[1]:1} | {changed[2]:1},')
        self.__prev_params = curr_params

    def __last_layer_params(self):
        return [component.layers[-1].get_weights() for component in self.all_components]


def components_changed(p_now, p_orig):
    w_now, b_now = p_now
    w_orig, b_orig = p_orig
    w_matrix = tf.math.equal(w_now, w_orig)
    b_matrix = tf.math.equal(b_now, b_orig)
    return not (np.all(w_matrix) and np.all(b_matrix))
