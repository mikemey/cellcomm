import os

import pandas as pd

CELL_MATRIX_FILE = os.path.join(os.path.dirname(__file__),
                                '..', 'data', 'GSE122930_Sham_1_week_matrix.mtx')


def load_matrix(file):
    df = pd.read_csv(file, header=None, skiprows=3,
                     delim_whitespace=True, names=['gene', 'barcode', 'p'])
    return df.pivot_table(index='barcode', columns='gene', values='p', fill_value=0)


class CellTraining:
    def __init__(self, matrix_file=CELL_MATRIX_FILE, batch_size=32):
        self.batch_size = batch_size
        self.data = load_matrix(matrix_file)

    def sample_cell_data(self, random_seed=None):
        return self.data.sample(self.batch_size, random_state=random_seed)
