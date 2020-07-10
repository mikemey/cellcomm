import os
import pathlib
from datetime import datetime

import atexit
import matplotlib.pyplot as plt
import numpy as np
import sklearn.manifold as skm
import sklearn.decomposition as skc
from mpl_toolkits.mplot3d import Axes3D


def data_file(data_file_):
    return os.path.join(os.path.dirname(__file__), '..', 'data', data_file_)


RUN_ID = '07-10-xxxx-TAC-4-e15'
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
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{ts}] it: {it:6}  TOT: {sum(all_losses):6.3f}  G-L: {g_loss:6.3f}  E-L: {e_loss:6.3f}  D-L: {d_loss:6.3f}')


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


def cluster(trainer_, reduction_algo, show_plot=False, save_plot=True, name='', skip_steps=2):
    algo_name = type(reduction_algo).__name__.lower() + name
    full_id = f'{RUN_ID}_{algo_name}'
    plt.rc('lines', markersize=3)

    def create_plot(it, losses):
        print(f'-|-- calc {algo_name}... ', end='', flush=True)
        all_encodings = trainer_.network.encode_genes(trainer_.data, to_hot_vector=False)
        points = reduction_algo.fit_transform(all_encodings)

        fig = plt.figure(figsize=(12, 8))
        fig.suptitle(f'{full_id} {it:6}, L: {sum(losses):6.3f}', fontsize=12)
        plt.grid(True, linewidth=0.2)

        if np.shape(points)[1] == 2:
            plt.scatter(points[:, 0], points[:, 1])
            fig.tight_layout()
        if np.shape(points)[1] == 3:
            plt.scatter(points[:, 0], points[:, 1], c=points[:, 2])
            fig.tight_layout()
        if np.shape(points)[1] == 4:
            ax = Axes3D(fig)
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 3])
        return fig

    def intercept(it, losses):
        if (show_plot or save_plot) and (it % skip_steps) >= (skip_steps - 1):
            fig = create_plot(it, losses)
            if save_plot:
                fig.savefig(f'{LOG_DIR}/{full_id}_{str(it).zfill(4)}.png')
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
    import umap

    check_log_dir()
    trainer = CellTraining(data_file(MATRIX_FILES[1]), batch_size=128, encoding_size=15)
    # trainer.network.summary()
    # trainer.run(300, interceptor=combined_interceptor([
    #     print_losses,
    #     log_losses(),
    #     # cluster(trainer, reduction_algo=skm.Isomap(n_components=4, n_jobs=-1)),
    #     cluster(trainer, reduction_algo=skm.TSNE(n_components=3, n_jobs=-1), name='_3d', skip_steps=5),
    #     cluster(trainer, reduction_algo=skc.PCA(n_components=3), name='_3d'),
    #     cluster(trainer, reduction_algo=skc.PCA(n_components=4), name='_4d'),
    #     cluster(trainer, reduction_algo=umap.UMAP(n_components=2), name='_2d'),
    #     cluster(trainer, reduction_algo=umap.UMAP(n_components=3), name='_3d'),
    #     cluster(trainer, reduction_algo=umap.UMAP(n_components=4), name='_4d'),
    #     lambda _, __: print('-|')
    # ]))
