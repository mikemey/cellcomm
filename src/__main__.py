import os
import pathlib

import sklearn.manifold as skm
import umap

from cell_type_training import CellTraining
from training_interceptors import *


def data_file(data_file_):
    return os.path.join(os.path.dirname(__file__), '..', 'data', data_file_)


MATRIX_FILES = [
    'GSE122930_TAC_1_week_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_repA+B_matrix.mtx',
    'GSE122930_Sham_1_week_matrix.mtx',
    'GSE122930_Sham_4_weeks_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_small_sample.mtx'
]


def create_interceptors(run_id, trainer):
    log_dir = os.path.join('logs', run_id)
    ics = ParamInterceptors(log_dir, run_id)
    return combined_interceptor([
        ics.print_losses,
        ics.log_losses,
        # ics.plot(trainer, reduction_algo=skm.Isomap(n_components=4, n_jobs=-1)),
        ics.plot(trainer, reduction_algo=skm.TSNE(n_components=3, n_jobs=-1, random_state=0), name='_3d', skip_steps=10),
        # ics.plot(trainer, reduction_algo=skc.PCA(n_components=3, random_state=0), name='_3d'),
        # ics.plot(trainer, reduction_algo=skc.PCA(n_components=4, random_state=0), name='_4d'),
        ics.plot_rotate(trainer, reduction_algo=umap.UMAP(n_components=3, random_state=0), skip_steps=1),
        # ics.plot(trainer, reduction_algo=umap.UMAP(n_components=2, random_state=0), name='_2d', skip_steps=1),
        # ics.plot(trainer, reduction_algo=umap.UMAP(n_components=3, random_state=0), name='_3d', skip_steps=1),
        ics.plot(trainer, reduction_algo=umap.UMAP(n_components=4, random_state=0), name='_4d', skip_steps=1),
        lambda _, __: print('-|')
    ])


def check_log_dir(log_dir):
    log_path = pathlib.Path(log_dir)
    if log_path.exists():
        raise AssertionError(f'duplicate run-id, log-dir: {log_dir}')
    log_path.mkdir(parents=True)


RUN_ID_TEMPLATE = '07-10-{}{}-TAC4-enc{}'

if __name__ == '__main__':
    for encoding_size in range(13, 21):
        now = datetime.now()
        run_id = RUN_ID_TEMPLATE.format(now.hour, now.minute, encoding_size)

        check_log_dir(run_id)
        trainer = CellTraining(data_file(MATRIX_FILES[1]), batch_size=128, encoding_size=encoding_size)
        interceptors = create_interceptors(run_id, trainer)
        trainer.run(300, interceptor=interceptors)
