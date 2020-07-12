import os
import pathlib
from datetime import datetime

from cell_type_training import CellTraining, load_matrix
from training_interceptors import ParamInterceptors, combined_interceptor


def data_file(data_file_):
    return os.path.join(os.path.dirname(__file__), '..', 'data', data_file_)


def log_file(log_file_):
    return os.path.join('logs', log_file_)


MATRIX_FILES = [
    'GSE122930_TAC_1_week_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_repA+B_matrix.mtx',
    'GSE122930_Sham_1_week_matrix.mtx',
    'GSE122930_Sham_4_weeks_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_small_sample.mtx'
]


def create_interceptors(log_dir_, run_id_, trainer_):
    ics = ParamInterceptors(log_dir_, run_id_)
    return combined_interceptor([
        ics.print_losses,
        ics.log_losses,
        # ics.plot_clusters_on_data(trainer_),
        ics.plot_encodings_directly(trainer_),
        # lambda _, __: print('-|')
    ])


def check_log_dir(log_dir_):
    log_path = pathlib.Path(log_dir_)
    if log_path.exists():
        raise AssertionError(f'duplicate run-id, log-dir: {log_dir_}')
    log_path.mkdir(parents=True)


RUN_ID_TEMPLATE = '{}-TAC4-direct-enc_{}'

if __name__ == '__main__':
    data_source = load_matrix(data_file(MATRIX_FILES[1]))
    for encoding_size in range(3, 5):
        now = datetime.now().strftime('%m-%d-%H%M')
        run_id = RUN_ID_TEMPLATE.format(now, encoding_size)
        log_dir = log_file(run_id)

        check_log_dir(log_dir)
        trainer = CellTraining(data_source, batch_size=128, encoding_size=encoding_size)
        interceptors = create_interceptors(log_dir, run_id, trainer)
        trainer.run(300, interceptor=interceptors)
