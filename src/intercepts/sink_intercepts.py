import atexit

from .data_sink import DataSink


class SinkIntercepts:
    def __init__(self, log_dir):
        self.sink = DataSink(log_dir=log_dir)
        atexit.register(self.sink.drain_data)

    def save_losses(self):
        graph_id = 'losses'
        self.sink.add_graph_header(graph_id, ['iteration', 'total-loss', 'g-loss', 'e-loss', 'd-loss'])

        def store_record(it, all_losses):
            g_loss, e_loss, d_loss = all_losses
            self.sink.add_data(graph_id, [it, sum(all_losses), g_loss, e_loss, d_loss])

        return store_record

    def save_accuracy(self, trainer):
        graph_id = 'accuracy'
        self.sink.add_graph_header(graph_id, ['iteration', 'pos-pct', 'neg-pct'])

        def intercept(it, _):
            batch = trainer.sample_cell_data()
            batch_size = len(batch)
            tp_acc, tn_acc = trainer.network.evaluate_discriminator_accuracy(batch)
            self.sink.add_data(graph_id, [it, tp_acc / batch_size, tn_acc / batch_size])

        return intercept
