from typing import Callable, Any

import pandas as pd

from bigan_classify import ClassifyCellBiGan
from bigan_cont import ContinuousCellBiGan


def load_matrix(matrix_file, verbose=False):
    if verbose:
        print(f'============ Loading {matrix_file}...')
    df = pd.read_csv(matrix_file, header=None, skiprows=3,
                     delim_whitespace=True, names=['gene', 'barcode', 'p'])
    df = df.pivot_table(index='barcode', columns='gene', values='p', fill_value=0)
    if verbose:
        print(f'============ DONE! barcodes: {df.shape[0]}, genes: {df.shape[1]}')
    return df


def load_cells(cells_file, verbose=False):
    if verbose:
        print(f'============ Loading {cells_file}...')
    df = pd.read_csv(cells_file, index_col=0)
    if verbose:
        print(f'============ DONE! barcodes: {df.shape[0]}, genes: {df.shape[1]}')
    return df


class CellTraining:
    def __init__(self, data, batch_size, encoding_size):
        self.batch_size = batch_size
        self.data = data
        self.network = ContinuousCellBiGan(encoding_size, gene_size=self.data.shape[1])
        # self.network = ClassifyCellBiGan(encoding_size, gene_size=self.data.shape[1])

    def sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)

    def run(self, iterations, interceptor: Callable[[int, Any], None] = None):
        for it in range(iterations):
            batch = self.sample_cell_data()
            step_result = self.network.trainings_step(batch)
            if interceptor:
                interceptor(it, step_result)
