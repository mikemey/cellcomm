from functools import reduce

from numpy import random

MAX_TRANSCRIPTS = pow(26, 3)


def generate_transcript_labels(count):
    if count > MAX_TRANSCRIPTS:
        raise AssertionError(f'too many transcripts: {count}')
    tcs = []
    char_range = range(65, 91)
    for i in char_range:
        for j in char_range:
            for k in char_range:
                tcs.append(f'{i:c}{j:c}{k:c}')
                if len(tcs) == count:
                    return tcs


class CellType:
    def __init__(self, name, t_dists):
        self.name = name
        self.transcript_dists = t_dists

    def __str__(self):
        dists = reduce(lambda cumulated, ts: f'{cumulated}\n\t{ts}', self.transcript_dists)
        return f'Cell type "{self.name}":\n{dists}'


class CellTranscript:
    def __init__(self, label, mean, sd):
        self.label = label
        self.mean = mean
        self.sd = sd

    def __str__(self):
        return f'Transcript "{self.label}" mean: {self.mean}, std-dev: {self.sd}'


def generate_cell_type(type_name, tc_labels, expressed_ratio, dist_range, dist_variance):
    expressed_size = int(len(tc_labels) * expressed_ratio)
    selected = random.choice(tc_labels, expressed_size, replace=False)
    tc_dists = [CellTranscript(label, random.randint(*dist_range), random.randint(*dist_variance))
                for label in selected]
    return CellType(type_name, tc_dists)
