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

    @abstractmethod
    def random_encoding_vector(self, batch_size):
        pass

    def random_uniform_vector(self, batch_size):
        return tf.random.uniform(shape=(batch_size, self.encoding_size), minval=0, maxval=1)

    @final
    def generate_cells(self, encoding_in, random_in=None):
        if random_in is None:
            random_in = self.random_uniform_vector(len(encoding_in))
        prediction = self._generator.predict((encoding_in, random_in))
        return tf.math.round(prediction)

    @abstractmethod
    def trainings_step(self, sampled_batch):
        pass

    def evaluate_discriminator_accuracy(self, sampled_batch):
        """
            return format: ( true-positives, true-negatives )
        """
        batch_size = len(sampled_batch)
        random_encodings = self.random_encoding_vector(batch_size)
        generated_cells = self.generate_cells(random_encodings)
        result = self._discriminator.predict((random_encodings, generated_cells), use_multiprocessing=True)
        false_negatives = np.count_nonzero(np.round(result))

        encodings = self.encoding_prediction(sampled_batch)
        result = self._discriminator.predict((encodings, sampled_batch), use_multiprocessing=True)
        true_positives = np.count_nonzero(np.round(result))

        return true_positives, batch_size - false_negatives

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
