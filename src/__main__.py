import os
import pathlib

import atexit
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


def data_file(data_file_):
    return os.path.join(os.path.dirname(__file__), '..', 'data', data_file_)


RUN_ID = 'delme'
# RUN_ID = '07-08-1720-TAC_4-mse-adam'
LOG_DIR = os.path.join('logs', RUN_ID)
MATRIX_FILES = [
    'GSE122930_TAC_1_week_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_repA+B_matrix.mtx',
    'GSE122930_Sham_1_week_matrix.mtx',
    'GSE122930_Sham_4_weeks_repA+B_matrix.mtx',
    'GSE122930_TAC_4_weeks_small_sample.mtx'
]


def check_log_dir():
    log_path = pathlib.Path(LOG_DIR)
    if log_path.exists():
        raise AssertionError(f'duplicate run-id, log-dir: {LOG_DIR}')
    log_path.mkdir()


def print_losses(it, all_losses):
    g_loss, e_loss, d_loss = all_losses
    print(f'it:{it:7}  TOT: {sum(all_losses):6.3f}  G-L: {g_loss:6.3f}  E-L: {e_loss:6.3f}  D-L: {d_loss:6.3f}')


def log_losses():
    from support.data_sink import DataSink

    losses_graph_id = 'losses'
    sink = DataSink(log_dir=LOG_DIR)
    sink.add_graph_header(losses_graph_id, ['iteration', 'total-loss', 'g-loss', 'e-loss', 'd-loss'])
    atexit.register(sink.drain_data)

    def add_losses(it, all_losses):
        g_loss, e_loss, d_loss = all_losses
        sink.add_data(losses_graph_id, [it, sum(all_losses), g_loss, e_loss, d_loss])

    return add_losses


def cluster(trainer_, show_plot=False, save_plot=True):
    def create_plot():
        print('calculate all encodings... ', end='')
        all_encodings = trainer_.network.predict_encoding(trainer_.data)
        print('done')

        print('calculate t-SNE... ', end='')
        points = TSNE(n_components=3).fit_transform(all_encodings)
        print('done')

        print('plotting points... ', end='')
        fig = plt.figure(figsize=(12, 8))
        plt.grid(True, linewidth=0.2)
        plt.scatter(points[:, 0], points[:, 1], c=points[:, 2])
        fig.tight_layout()
        return fig

    def intercept(it, _):
        count = it + 1
        if (show_plot or save_plot) and it > 50 and (count % 20) == 0:
            fig = create_plot()
            if save_plot:
                fig.savefig(f'{LOG_DIR}/t-sne-cluster-{str(it).zfill(4)}.png')
            if show_plot:
                plt.show()
            plt.close(fig)

    return intercept


def combined_interceptor(interceptors):
    def call_all(it, all_losses):
        for ic in interceptors:
            ic(it, all_losses)

    return call_all


if __name__ == '__main__':
    from cell_type_training import CellTraining

    check_log_dir()
    trainer = CellTraining(data_file(MATRIX_FILES[1]), batch_size=128, encoding_size=20)
    trainer.run(9001, interceptor=combined_interceptor([
        print_losses,
        log_losses(),
        cluster(trainer)
    ]))
