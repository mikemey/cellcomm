#!/usr/bin/env python3
import pickle

import atexit
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from multiprocessing import Pool

from mpl_toolkits.mplot3d import Axes3D

POINTS_SIZE = 0.2
GRAPH_2D_ID = '2D'
GRAPH_3D_ID = '3D'

if len(sys.argv) < 2:
    print('\nrequired \'run-id\'')
    exit(-1)

run_id = sys.argv[1]
log_dir = f'logs/{run_id}'
encodings_dir = f'{log_dir}/encodings'
plots_dir = f'{log_dir}/plots'


def load_coords(iteration):
    with open(f'{encodings_dir}/{iteration}.enc', 'rb') as f:
        encodings = pickle.load(f)
        return np.multiply(encodings, 255)


def plot_file_template(graph_type, iteration):
    return f'{plots_dir}/{run_id}_{graph_type}_{iteration}.png'


def video_file_template(graph_type):
    return f'{log_dir}/{run_id}_{graph_type}.mp4'


def save_as_graph(iteration, coords):
    def figure_file(graph_type):
        return plot_file_template(graph_type, str(iteration).zfill(5))

    def create_figure(graph_type):
        plt.rc('lines', markersize=POINTS_SIZE)

        fig_ = plt.figure(figsize=(12, 8))
        fig_.suptitle(f'{run_id} {graph_type} {iteration:6}', fontsize=12)
        plt.grid(True, linewidth=0.2)
        return fig_

    fig = create_figure(GRAPH_2D_ID)
    for ax in fig.axes:
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 255)
    plt.scatter(coords[:, 0], coords[:, 1], c=coords[:, 2])
    fig.tight_layout()
    fig.savefig(figure_file(GRAPH_2D_ID))
    plt.close(fig)

    fig = create_figure(GRAPH_3D_ID)
    ax = Axes3D(fig)
    ax.set_xlim3d(0, 255)
    ax.set_ylim3d(0, 255)
    ax.set_zlim3d(0, 255)
    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=POINTS_SIZE)
    fig.savefig(figure_file(GRAPH_3D_ID))
    plt.close(fig)


def convert_encodings(iteration):
    coords = load_coords(iteration)
    save_as_graph(iteration, coords)
    print(f'[{iteration}] ', end='', flush=True)


def convert_images_to_video(graph_type):
    img_pattern = plot_file_template(graph_type, '*')
    video_file = video_file_template(graph_type)
    os.system(f'ffmpeg -v fatal -stats -r 5 -pattern_type glob -i "{img_pattern}" -vcodec mpeg4 -y {video_file}')


if __name__ == '__main__':
    print('converting encodings to graphs... ', end='')
    encoding_files = os.listdir(encodings_dir)
    iterations = [(enc_file.rstrip('.enc'),) for enc_file in encoding_files]
    print(f'{len(iterations)} found')

    pool = Pool(processes=6)
    atexit.register(pool.close)
    pool.starmap(convert_encodings, iterations)
    print()
    pool.close()
    print('converting 2D graphs to mp4...')
    convert_images_to_video(GRAPH_2D_ID)
    print('converting 3D graphs to mp4...')
    convert_images_to_video(GRAPH_3D_ID)
    print('DONE')
