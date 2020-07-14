from abc import abstractmethod
from typing import final, Callable

import numpy as np
import tensorflow as tf
from tensorflow.python.keras import Model
from copy import deepcopy


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
    def generate_cells(self, encoding_in, random_in):
        prediction = self._generator.predict((encoding_in, random_in))
        return tf.math.round(prediction)

    @abstractmethod
    def trainings_step(self, sampled_batch):
        pass

    def print_params_changes(self, msg):
        curr_params = self.__last_layer_params()
        changed = [components_changed(p_now, p_orig) for p_now, p_orig in zip(curr_params, self.__prev_params)]
        print(msg, 'G|E|D changed:', f'{changed[0]:1} | {changed[1]:1} | {changed[2]:1},')
        self.__prev_params = curr_params

    def __last_layer_params(self):
        def collect_weights(component):
            collected_weights = []
            for lay in component.layers:
                if len(lay.get_weights()) == 2:
                    for weights in lay.get_weights():
                        collected_weights.append(deepcopy(weights))
            return collected_weights

        return list(map(collect_weights, self.all_components))


def components_changed(p_now, p_orig):
    for n, o in zip(p_now, p_orig):
        equality_matrix = tf.math.equal(n, o)
        if not np.all(equality_matrix):
            return True
    return False
