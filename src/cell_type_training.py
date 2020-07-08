import os
from typing import Callable, Any

import pandas as pd

from cell_bigan import CellBiGan
from support.data_sink import DataSink

LOSSES_GRAPH_ID = 'losses'


def load_matrix(file):
    df = pd.read_csv(file, header=None, skiprows=3,
                     delim_whitespace=True, names=['gene', 'barcode', 'p'])
    df = df.pivot_table(index='barcode', columns='gene', values='p', fill_value=0)
    print(f'============ Loaded {file}')
    print(f'============ barcodes: {df.shape[0]}, genes: {df.shape[1]}')
    print('=' * 80)
    return df


class CellSinkAdapter:
    def __init__(self, run_id, write_log):
        self.write_log = write_log
        if self.write_log:
            log_dir = os.path.join('logs', run_id)
            self.sink = DataSink(log_dir=log_dir)
            self.sink.add_graph_header(LOSSES_GRAPH_ID, ['iteration', 'total-loss', 'g-loss', 'e-loss', 'd-loss'])

    def add_losses(self, *data):
        if self.write_log:
            self.sink.add_data(LOSSES_GRAPH_ID, list(data))

    def drain_data(self):
        if self.write_log:
            self.sink.drain_data()


class CellTraining:
    def __init__(self, run_id, matrix_file, batch_size, encoding_size, write_log=True):
        self.batch_size = batch_size
        self.data = load_matrix(matrix_file)
        self.network = CellBiGan(encoding_size, gene_size=self.data.shape[1])
        self.sink = CellSinkAdapter(run_id, write_log)

    def _sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)

    def run(self, iterations, interceptor: Callable[[int, Any], None] = None):
        for it in range(iterations):
            batch = self._sample_cell_data()
            all_losses = g_loss, e_loss, d_loss = self.network.trainings_step(batch)
            if interceptor:
                interceptor(it, all_losses)
            total_loss = sum(all_losses)
            self.sink.add_losses(it, total_loss, g_loss, e_loss, d_loss)
            print(f'it:{it:7}  TOT: {total_loss:6.3f}  G-L: {g_loss:6.3f}  E-L: {e_loss:6.3f}  D-L: {d_loss:6.3f}')
        self.sink.drain_data()
