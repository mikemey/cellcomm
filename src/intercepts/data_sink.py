from typing import Any, Iterable

DEFAULT_LOG_DIR = 'logs'
DEFAULT_BATCH_SIZE = 1

FILE_KEY = 'file'
LINES_KEY = 'lines'
SIZE_KEY = 'size'


def csv_line(values):
    return ','.join(str(s) for s in values) + '\n'


class DataSink:
    def __init__(self, log_dir=DEFAULT_LOG_DIR, batch_size=DEFAULT_BATCH_SIZE):
        self.__log_dir = log_dir
        self.__graphs = {}
        self.__batch_size = batch_size

    def add_graph_header(self, graph_id, fields: Iterable[Any]):
        if graph_id in self.__graphs.keys():
            raise AssertionError(f'duplicate graph name: {graph_id}')

        self.__graphs[graph_id] = {
            FILE_KEY: f'{self.__log_dir}/{graph_id}.csv',
            LINES_KEY: [],
            SIZE_KEY: len(fields)
        }
        self.__write_file_line(graph_id, csv_line(fields))

    def add_data(self, graph_id, values: Iterable[Any]):
        if graph_id not in self.__graphs:
            raise AssertionError(f'unknown graph: {graph_id}')

        graph_data = self.__graphs[graph_id]
        if not len(values) == graph_data[SIZE_KEY]:
            raise AssertionError(f'expected {graph_data[SIZE_KEY]} values, received: {values}')

        file_lines = graph_data[LINES_KEY]
        file_lines.append(csv_line(values))

        if len(file_lines) >= self.__batch_size:
            self.__drain_graph_data(graph_id)

    def drain_data(self):
        for graph_id in self.__graphs.keys():
            self.__drain_graph_data(graph_id)

    def __drain_graph_data(self, graph_id):
        graph_data = self.__graphs[graph_id]
        if len(graph_data[LINES_KEY]) > 0:
            file_lines = graph_data[LINES_KEY]
            data = ''.join(file_lines)
            self.__write_file_line(graph_id, data)
            file_lines.clear()

    def __write_file_line(self, graph_id, data):
        with open(self.__graphs[graph_id][FILE_KEY], 'a+') as graph_f:
            graph_f.write(data)
