import os
import pathlib
import signal
from datetime import datetime

import sys

from cell_type_training import CellTraining, load_matrix
from db_recorder import DbRecorder
from training_interceptors import ParamInterceptors, combined_interceptor, skip_iterations, offset_iterations


def data_file(file):
    return os.path.join(os.path.dirname(__file__), '..', 'data', file)


def log_file(log_file_):
    return os.path.join('logs', log_file_)


def build_source(source_id):
    return {
        'matrix': data_file(f'{source_id}_matrix.mtx'),
        'barcodes': data_file(f'{source_id}_barcodes.tsv'),
        'genes': data_file(f'{source_id}_genes.tsv')
    }


SOURCE_IDS = [
    'GSE122930_TAC_1_week_repA+B',
    'GSE122930_TAC_4_weeks_repA+B',
    'GSE122930_Sham_1_week',
    'GSE122930_Sham_4_weeks_repA+B'
]

SOURCES = [build_source(src) for src in SOURCE_IDS]


def create_interceptors(log_dir, run_id, trainer, sources):
    ics = ParamInterceptors(log_dir, run_id)
    db_rec = DbRecorder(run_id, sources)
    db_rec.store_encoding_run()
    db_rec.load_barcodes()
    return combined_interceptor([
        ics.print_losses,
        ics.save_losses(),
        offset_iterations(1000, skip_iterations(40, db_rec.create_interceptor(trainer)))
        # lambda _, __: print('-|')
    ])


def check_log_dir(log_dir):
    log_path = pathlib.Path(log_dir)
    if log_path.exists():
        raise AssertionError(f'duplicate run-id, log-dir: {log_dir}')
    log_path.mkdir(parents=True)


RUN_ID = 'TAC4-LWR20000'
DATA_SOURCE = SOURCES[1]
LOG_ID_TEMPLATE = '{}_' + RUN_ID + '_e{}'


def run_training(batch_size=128):
    data_source = load_matrix(DATA_SOURCE['matrix'], verbose=True)
    encoding_size = 3
    now = datetime.now().strftime('%m-%d-%H%M')
    log_dir = log_file(LOG_ID_TEMPLATE.format(now, encoding_size))

    check_log_dir(log_dir)
    trainer = CellTraining(data_source, batch_size=batch_size, encoding_size=encoding_size)
    interceptors = create_interceptors(log_dir, RUN_ID, trainer, DATA_SOURCE)
    trainer.run(20000, interceptor=interceptors)


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
