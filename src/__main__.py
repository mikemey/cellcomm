import os

from cell_type_training import CellTraining


def data_file(data_file_):
    return os.path.join(os.path.dirname(__file__), '..', 'data', data_file_)


MATRIX_FILES = [
    'GSE122930_TAC_1_week_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_repA+B_matrix.mtx',
    'GSE122930_Sham_1_week_matrix.mtx',
    'GSE122930_Sham_4_weeks_repA+B_matrix.mtx',
]

trainer = CellTraining('07-07-long-run', data_file(MATRIX_FILES[0]),
                       batch_size=128, encoding_size=20)
# trainer.bigan.summary()
trainer.run(20000)
