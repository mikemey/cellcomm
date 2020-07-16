import os
import pathlib
import signal
from datetime import datetime

import sys

from cell_type_training import CellTraining, load_matrix
from training_interceptors import ParamInterceptors, combined_interceptor, skip_iterations


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

CELL_FILES = [
    'GSE122930_TAC_1_week.cell',
    'GSE122930_TAC_4_weeks.cell',
    'GSE122930_Sham_1_week.cell',
    'GSE122930_Sham_4_weeks.cell',
    'GSE122930_TAC_4_weeks_small.cell'
]


def create_interceptors(log_dir_, run_id_, trainer_):
    ics = ParamInterceptors(log_dir_, run_id_)
    return combined_interceptor([
        ics.print_losses,
        ics.log_losses(),
        skip_iterations(ics.log_accuracy(trainer_), 10),
        # ics.plot_clusters_on_data(trainer_),
        skip_iterations(ics.plot_encodings_directly(trainer_), 100),
        # ics.save_gene_sample(trainer_),
        # lambda _, __: print('-|')
    ])


def check_log_dir(log_dir_):
    log_path = pathlib.Path(log_dir_)
    if log_path.exists():
        raise AssertionError(f'duplicate run-id, log-dir: {log_dir_}')
    log_path.mkdir(parents=True)


RUN_ID_TEMPLATE = '{}_TAC4-LR9990-e_{}'


def run_training(source_file=MATRIX_FILES[1], batch_size=128):
    data_source = load_matrix(data_file(source_file), verbose=True)
    for encoding_size in range(3, 4):
        now = datetime.now().strftime('%m-%d-%H%M')
        run_id = RUN_ID_TEMPLATE.format(now, encoding_size)
        log_dir = log_file(run_id)

        check_log_dir(log_dir)
        trainer = CellTraining(data_source, batch_size=batch_size, encoding_size=encoding_size)
        # trainer.network.summary()
        interceptors = create_interceptors(log_dir, run_id, trainer)
        trainer.run(9990, interceptor=interceptors)


def store_converted_cell_file(matrix_file, cell_file):
    print('converting matrix file:')
    df = load_matrix(matrix_file, verbose=True)
    print('storing cell file:', cell_file, '... ', end='', flush=True)
    df.to_csv(cell_file)
    print('done')


def signal_handler(_, __):
    print('\tstopped')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'convert':
            assert len(sys.argv) == 4, 'required parameters missing: convert <source-matrix-file> <convert-target-file>'
            store_converted_cell_file(sys.argv[2], sys.argv[3])
        else:
            print('unrecognised command:', cmd)
    else:
        run_training()
