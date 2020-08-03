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
    def __init__(self, data, batch_size, encoding_size, batches_per_iteration=10):
        self.batch_size = batch_size
        self.data = data
        self.batches_per_iteration = batches_per_iteration
        self.network = ContinuousCellBiGan(encoding_size, gene_size=self.data.shape[1])
        # self.network = ClassifyCellBiGan(encoding_size, gene_size=self.data.shape[1])

    def sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)

    def run(self, iterations, interceptor: Callable[[int, Any], None] = None):
        for it in range(iterations):
            g_losses = e_losses = d_losses = 0
            for batch_it in range(self.batches_per_iteration):
                batch = self.sample_cell_data()
                gl, el, dl = self.network.trainings_step(batch)
                g_losses += gl
                e_losses += el
                d_losses += dl
            if interceptor:
                interceptor(it, (g_losses, e_losses, d_losses))
