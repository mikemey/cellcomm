from datetime import datetime

import atexit
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

from support.data_sink import DataSink


def combined_interceptor(interceptors):
    def call_all(it, all_losses):
        for ic in interceptors:
            ic(it, all_losses)

    return call_all


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

    def plot(self, trainer_, reduction_algo, show_plot=False, save_plot=True, name='', skip_steps=2):
        algo_name = type(reduction_algo).__name__.lower() + name
        full_id = f'{self.run_id}_{algo_name}'
        plt.rc('lines', markersize=2)

        def create_plot(it, losses):
            print(f'--|-- {algo_name}... ', end='', flush=True)
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
                    fig.savefig(f'{self.log_dir}/{full_id}_{str(it).zfill(4)}.png')
                if show_plot:
                    plt.show()
                plt.close(fig)

        return intercept

    def plot_rotate(self, trainer_, reduction_algo, skip_steps=2):
        algo_name = type(reduction_algo).__name__.lower()
        full_id = f'{self.run_id}_{algo_name}'
        plt.rc('lines', markersize=2)

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
                    fig = plt.figure(figsize=(12, 8))
                    fig.suptitle(f'{title} {it:6}, L: {sum(losses):6.3f}', fontsize=12)
                    plt.grid(True, linewidth=0.2)

                    plt.scatter(points[:, p_position[0]], points[:, p_position[1]], c=points[:, p_position[2]])
                    fig.tight_layout()
                    fig.savefig(f'{self.log_dir}/{title}_{str(it).zfill(4)}.png')
                    plt.close(fig)

        return intercept
