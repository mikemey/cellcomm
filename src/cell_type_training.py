from typing import Callable, Any

import pandas as pd

from cell_bigan import CellBiGan


def load_matrix(file):
    df = pd.read_csv(file, header=None, skiprows=3,
                     delim_whitespace=True, names=['gene', 'barcode', 'p'])
    df = df.pivot_table(index='barcode', columns='gene', values='p', fill_value=0)
    print(f'============ Loaded {file}')
    print(f'============ barcodes: {df.shape[0]}, genes: {df.shape[1]}')
    print('=' * 80)
    return df


class CellTraining:
    def __init__(self, matrix_file, batch_size, encoding_size):
        self.batch_size = batch_size
        self.data = load_matrix(matrix_file)
        self.network = CellBiGan(encoding_size, gene_size=self.data.shape[1])

    def _sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)

    def run(self, iterations, interceptor: Callable[[int, Any], None] = None):
        for it in range(iterations):
            batch = self._sample_cell_data()
            step_result = self.network.trainings_step(batch)
            if interceptor:
                interceptor(it, step_result)
