import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn.manifold as skm
import umap
from mpl_toolkits.mplot3d import Axes3D
from tensorflow import convert_to_tensor
from tensorflow.python.keras import backend

POINTS_SIZE = 0.3


def create_default_figure(title, it, losses):
    plt.rc('lines', markersize=POINTS_SIZE)

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(f'{title} {it:6}, L: {sum(losses):6.3f}', fontsize=12)
    plt.grid(True, linewidth=0.2)
    return fig


class PlotIntercepts:
    def __init__(self, log_dir, run_id):
        self.log_dir = log_dir
        self.run_id = run_id

        self.plots_dir = f'{self.log_dir}/plots'
        pathlib.Path(self.plots_dir).mkdir()

    def __figure_path(self, title, iteration):
        return f'{self.plots_dir}/{title}_{str(iteration).zfill(4)}.png'

    def plot_fully(self, trainer, reduction_algo, show_plot=False, save_plot=True, name=''):
        algo_name = type(reduction_algo).__name__.lower() + name
        full_id = f'{self.run_id}_{algo_name}'

        def create_plot(it, losses):
            print(f'--|-- {algo_name}... ', end='', flush=True)
            all_encodings = trainer.network.encoding_prediction(trainer.data)
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
                ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 3], s=POINTS_SIZE)
            return fig

        def intercept(it, losses):
            fig = create_plot(it, losses)
            if save_plot:
                fig.savefig(self.__figure_path(full_id, it))
            if show_plot:
                plt.show()
            plt.close(fig)

        return intercept

    def plot_rotate(self, trainer, reduction_algo):
        algo_name = type(reduction_algo).__name__.lower()
        full_id = f'{self.run_id}_{algo_name}'

        rot_ixs = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]

        def intercept(it, losses):
            print(f'--|-- {algo_name}... ', end='', flush=True)
            all_encodings = trainer.network.encoding_prediction(trainer.data)
            points = reduction_algo.fit_transform(all_encodings)
            for p_ix, p_position in enumerate(rot_ixs):
                title = f'{full_id}_pos{p_ix}'
                fig = create_default_figure(title, it, losses)

                plt.scatter(points[:, p_position[0]], points[:, p_position[1]], c=points[:, p_position[2]])
                fig.tight_layout()
                fig.savefig(self.__figure_path(title, it))
                plt.close(fig)

        return intercept

    def plot_clusters_on_data(self, trainer):
        algo_metas = [(skm.TSNE, 'tsne'), (umap.UMAP, 'umap')]

        all_2d_points = [create_2d_points(*a_meta, trainer.data) for a_meta in algo_metas]
        print(f'- Done')

        def intercept(it, losses):
            all_encodings = trainer.network.encoding_prediction(trainer.data)
            all_color_points = [run_fit_transform(*a_meta, all_encodings) for a_meta in algo_metas]

            for a_meta, xy_points, color_points in zip(algo_metas, all_2d_points, all_color_points):
                full_id = f'{self.run_id}_{a_meta[1]}'
                fig = create_default_figure(full_id, it, losses)
                plt.scatter(xy_points[:, 0], xy_points[:, 1], c=color_points)
                fig.tight_layout()
                fig.savefig(self.__figure_path(full_id, it))
                plt.close(fig)

        return intercept

    def plot_encodings_directly(self, trainer):
        def intercept(it, losses):
            encodings = trainer.network.encoding_prediction(trainer.data)
            enc_dim = np.shape(encodings)[1]
            coords = np.multiply(encodings, 255)

            if enc_dim == 3:
                title = f'{self.run_id}_2Dc'
                fig = create_default_figure(title, it, losses)
                for ax in fig.axes:
                    ax.set_xlim(0, 255)
                    ax.set_ylim(0, 255)
                plt.scatter(coords[:, 0], coords[:, 1], c=coords[:, 2])
                fig.tight_layout()
                fig.savefig(self.__figure_path(title, it))
                plt.close(fig)

                title = f'{self.run_id}_3Dm'
                fig = create_default_figure(title, it, losses)
                ax = Axes3D(fig)
                ax.set_xlim3d(0, 255)
                ax.set_ylim3d(0, 255)
                ax.set_zlim3d(0, 255)
                ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=POINTS_SIZE)
                fig.savefig(self.__figure_path(title, it))
                plt.close(fig)

            if enc_dim == 4:
                title = f'{self.run_id}_3Dc'
                fig = create_default_figure(title, it, losses)
                ax = Axes3D(fig)
                ax.set_xlim3d(0, 255)
                ax.set_ylim3d(0, 255)
                ax.set_zlim3d(0, 255)
                ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], c=coords[:, 3], s=POINTS_SIZE)
                fig.savefig(self.__figure_path(title, it))
                plt.close(fig)

        return intercept

    def save_gene_sample(self, trainer):
        encodings_in = convert_to_tensor(permuted_vector(trainer.network.encoding_size, 2))
        noise = trainer.network.random_uniform_vector(len(encodings_in))

        def intercept(it, _):
            if it in [0, 9, 49, 99, 199]:
                cell_predictions = trainer.network.generate_cells(encodings_in, noise)
                data = backend.eval(cell_predictions)
                df = pd.DataFrame.from_records(data)
                df.to_csv(f'{self.log_dir}/{self.run_id}_cells_{str(it).zfill(4)}.csv')

        return intercept


def permuted_vector(v_width, copies_per_v):
    coll = []
    for i in range(v_width):
        cat = np.zeros(v_width)
        cat[i] = 1.0
        coll.extend([cat] * copies_per_v)
    return coll


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
