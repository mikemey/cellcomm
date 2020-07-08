import os

import atexit


def data_file(data_file_):
    return os.path.join(os.path.dirname(__file__), '..', 'data', data_file_)


# RUN_ID = 'delme'
RUN_ID = '07-08-1237-TAC_4-bxe-adam-soft'
MATRIX_FILES = [
    'GSE122930_TAC_1_week_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_repA+B_matrix.mtx',
    'GSE122930_Sham_1_week_matrix.mtx',
    'GSE122930_Sham_4_weeks_repA+B_matrix.mtx'
]


def print_losses(it, all_losses):
    g_loss, e_loss, d_loss = all_losses
    print(f'it:{it:7}  TOT: {sum(all_losses):6.3f}  G-L: {g_loss:6.3f}  E-L: {e_loss:6.3f}  D-L: {d_loss:6.3f}')


def log_losses():
    from support.data_sink import DataSink

    losses_graph_id = 'losses'
    log_dir = os.path.join('logs', RUN_ID)

    sink = DataSink(log_dir=log_dir)
    sink.add_graph_header(losses_graph_id, ['iteration', 'total-loss', 'g-loss', 'e-loss', 'd-loss'])
    atexit.register(sink.drain_data)

    def add_losses(it, all_losses):
        g_loss, e_loss, d_loss = all_losses
        sink.add_data(losses_graph_id, [it, sum(all_losses), g_loss, e_loss, d_loss])

    return add_losses


def combined_interceptor(interceptors):
    def call_all(it, all_losses):
        for ic in interceptors:
            ic(it, all_losses)

    return call_all


if __name__ == '__main__':
    from cell_type_training import CellTraining

    trainer = CellTraining(data_file(MATRIX_FILES[1]), batch_size=128, encoding_size=20)
    write_log_losses = log_losses()

    trainer.run(20000, interceptor=combined_interceptor([
        print_losses,
        write_log_losses
    ]))
