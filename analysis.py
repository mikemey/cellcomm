import matplotlib.pyplot as plt

run_id = '07-07-mse-rms0002'
save_image = False
show_plot = True


def read_log_lines(log_file):
    return log_file.readlines()[1:]


def clean(token):
    return float(token.strip())


with open(f'logs/{run_id}/losses.csv') as f:
    xs = []
    all_loss_graphs = [[], [], [], []]
    for line in read_log_lines(f):
        tokens = map(clean, line.split(','))
        it, total_loss, g_loss, e_loss, d_loss = list(tokens)
        xs.append(it)
        all_loss_graphs[0].append(total_loss)
        all_loss_graphs[1].append(g_loss)
        all_loss_graphs[2].append(e_loss)
        all_loss_graphs[3].append(d_loss)

plt.rc('font', size=3)
plt.rc('lines', lw=0.2)
plt.rc('axes', lw=0.25)
plt.rc('xtick.major', width=0.2)
plt.rc('ytick.major', width=0.2)

fig = plt.figure(figsize=(4, 2.2), dpi=400)

plt.plot(xs, all_loss_graphs[0], '-k', label='total')
plt.plot(xs, all_loss_graphs[1], '-b', label='generator')
plt.plot(xs, all_loss_graphs[2], '-g', label='encoder')
plt.plot(xs, all_loss_graphs[3], '-r', label='discriminator')

plt.grid(True, linewidth=0.2)
plt.xlim(xmin=0, xmax=max(xs) + 1)
plt.ylim(ymin=0)
legend_frame = plt.legend(title='Losses', framealpha=1.0).get_frame()
legend_frame.set_linewidth(0.4)

fig.tight_layout()
if save_image:
    fig.savefig(f'docs/{run_id}_losses.png')
if show_plot:
    plt.show()
plt.close(fig)
