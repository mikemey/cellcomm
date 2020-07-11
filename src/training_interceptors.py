from datetime import datetime

import atexit
import matplotlib.pyplot as plt
import numpy as np
import sklearn.manifold as skm
import umap
from mpl_toolkits.mplot3d import Axes3D

from support.data_sink import DataSink


def combined_interceptor(interceptors):
    def call_all(it, all_losses):
        for ic in interceptors:
            ic(it, all_losses)

    return call_all


def create_default_figure(title, it, losses):
    plt.rc('lines', markersize=2)

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(f'{title} {it:6}, L: {sum(losses):6.3f}', fontsize=12)
    plt.grid(True, linewidth=0.2)
    return fig


LOSSES_ID = 'losses'


class ParamInterceptors:
    def __init__(self, log_dir, run_id):
        self.log_dir = log_dir
        self.run_id = run_id
        self.sink = DataSink(log_dir=self.log_dir)
        self.sink.add_graph_header(LOSSES_ID, ['iteration', 'total-loss', 'g-loss', 'e-loss', 'd-loss'])
        atexit.register(self.sink.drain_data)

    def print_losses(self, it, all_losses):
        g_loss, e_loss, d_loss = all_losses
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{ts}] {self.run_id} it: {it:6}  TOT: {sum(all_losses):6.3f}  G-L: {g_loss:6.3f}  E-L: {e_loss:6.3f}  D-L: {d_loss:6.3f}')

    def log_losses(self, it, all_losses):
        g_loss, e_loss, d_loss = all_losses
        self.sink.add_data(LOSSES_ID, [it, sum(all_losses), g_loss, e_loss, d_loss])

    def plot_fully(self, trainer_, reduction_algo, show_plot=False, save_plot=True, name='', skip_steps=2):
        algo_name = type(reduction_algo).__name__.lower() + name
        full_id = f'{self.run_id}_{algo_name}'

        def create_plot(it, losses):
            print(f'--|-- {algo_name}... ', end='', flush=True)
            all_encodings = trainer_.network.encode_genes(trainer_.data, to_hot_vector=False)
            points = reduction_algo.fit_transform(all_encodings)
            fig = create_default_figure(full_id, it, losses)

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
                    fig.savefig(f'{self.log_dir}/{full_id}_{str(it).zfill(4)}.png')
                if show_plot:
                    plt.show()
                plt.close(fig)

        return intercept

    def plot_rotate(self, trainer_, reduction_algo, skip_steps=2):
        algo_name = type(reduction_algo).__name__.lower()
        full_id = f'{self.run_id}_{algo_name}'

        rot_ixs = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]

        def intercept(it, losses):
            if (it % skip_steps) >= (skip_steps - 1):
                print(f'--|-- {algo_name}... ', end='', flush=True)
                all_encodings = trainer_.network.encode_genes(trainer_.data, to_hot_vector=False)
                points = reduction_algo.fit_transform(all_encodings)
                for p_ix, p_position in enumerate(rot_ixs):
                    title = f'{full_id}_pos{p_ix}'
                    fig = create_default_figure(title, it, losses)

                    plt.scatter(points[:, p_position[0]], points[:, p_position[1]], c=points[:, p_position[2]])
                    fig.tight_layout()
                    fig.savefig(f'{self.log_dir}/{title}_{str(it).zfill(4)}.png')
                    plt.close(fig)

        return intercept

    def plot_clusters_on_data(self, trainer_):
        algo_metas = [(skm.TSNE, 'tsne'), (umap.UMAP, 'umap')]

        all_2d_points = [create_2d_points(*a_meta, trainer_.data) for a_meta in algo_metas]
        print(f'- Done')

        def intercept(it, losses):
            all_encodings = trainer_.network.encode_genes(trainer_.data, to_hot_vector=False)
            all_color_points = [run_fit_transform(*a_meta, all_encodings) for a_meta in algo_metas]

            for a_meta, xy_points, color_points in zip(algo_metas, all_2d_points, all_color_points):
                full_id = f'{self.run_id}_{a_meta[1]}'
                fig = create_default_figure(full_id, it, losses)
                plt.scatter(xy_points[:, 0], xy_points[:, 1], c=color_points)
                fig.tight_layout()
                fig.savefig(f'{self.log_dir}/{full_id}_{str(it).zfill(4)}.png')
                plt.close(fig)

        return intercept


def create_2d_points(algo_class, algo_name, data):
    print(f'calculating 2D "{algo_name}"... ', end='', flush=True)
    points = create_algo(algo_class, n_components=2).fit_transform(data)
    print(f'"{algo_name}" ok ', end='', flush=True)
    return points


def run_fit_transform(algo_class, algo_name, encodings):
    print(f'--|-- {algo_name} ', end='', flush=True)
    color_points = create_algo(algo_class, n_components=1).fit_transform(encodings)
    print(f'"{algo_name}" ok ', end='', flush=True)
    return color_points


def create_algo(algo_class, n_components):
    try:
        return algo_class(n_components=n_components, random_state=0, n_jobs=-1)
    except TypeError:
        return algo_class(n_components=n_components, random_state=0)
