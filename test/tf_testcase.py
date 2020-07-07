import unittest

import numpy as np
import tensorflow as tf


class TFTestCase(unittest.TestCase):
    def assertDeepEqual(self, expected, actual):
        eq_matrix = tf.math.equal(expected, actual)
        self.assertTrue(np.all(eq_matrix), f'\tExpected:\n{expected}\n\tActual:\n{actual}')
