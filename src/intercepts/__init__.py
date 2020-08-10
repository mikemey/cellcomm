from datetime import datetime

from .plot_intercepts import PlotIntercepts
from .sink_intercepts import SinkIntercepts


def combined_interceptors(interceptors):
    def call_all(it, losses):
        for ic in interceptors:
            ic(it, losses)

    return call_all


def skip_iterations(steps, interceptor):
    def intercept(it, losses):
        if (it % steps) >= (steps - 1):
            interceptor(it, losses)

    return intercept


def offset_iterations(offset, interceptor):
    def intercept(it, losses):
        if it >= offset:
            interceptor(it, losses)

    return intercept


def print_losses(full_run_id):
    def intercept(it, all_losses):
        g_loss, e_loss, d_loss = all_losses
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{ts}] {full_run_id} it: {it:6}  TOT: {sum(all_losses):6.3f}  G-L: {g_loss:6.3f}  E-L: {e_loss:6.3f}  D-L: {d_loss:6.3f}')

    return intercept
