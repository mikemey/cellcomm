#!/usr/bin/env python3
import matplotlib.pyplot as plt
import sys
import numpy as np

if len(sys.argv) < 2:
    print('\nrequired \'run-id\'')
    exit(-1)

run_id = sys.argv[1]
save_image = False
show_plot = True


def read_log_lines(log_file):
    return log_file.readlines()[1:]


def clean(token):
    return float(token.strip())


with open(f'logs/{run_id}/accuracy.csv') as f:
    xs = []
    all_loss_graphs = [[], []]
    for line in read_log_lines(f):
        tokens = map(clean, line.split(','))
        it, pos_acc, neg_acc = list(tokens)
        xs.append(it)
        all_loss_graphs[0].append(np.round(pos_acc * 100))
        all_loss_graphs[1].append(np.round(neg_acc * 100))

fig = plt.figure(figsize=(14, 8))

plt.plot(xs, all_loss_graphs[0], '-g', label='positive')
plt.plot(xs, all_loss_graphs[1], '-r', label='negative')

plt.xlim(xmin=min(xs), xmax=max(xs) + 1)
plt.ylim(ymin=0, ymax=100)
legend_frame = plt.legend(title='Accuracy', framealpha=1.0).get_frame()

fig.tight_layout()
if save_image:
    fig.savefig(f'docs/{run_id}_accuracy.png')
if show_plot:
    plt.show()
plt.close(fig)
