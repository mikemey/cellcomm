from functools import reduce
from typing import List

from numpy import random, count_nonzero

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


class TranscriptDistribution:
    def __init__(self, label, mean, sd):
        self.label = label
        self.mean = mean
        self.sd = sd

    def __str__(self):
        return f'Transcript "{self.label}" mean: {self.mean}, std-dev: {self.sd}'


class CellType:
    def __init__(self, name, t_labels, t_dists: List[TranscriptDistribution]):
        self.name = name
        self.transcript_labels = t_labels
        self.transcript_dists = t_dists

    def __str__(self):
        ts_as_str = map(str, self.transcript_dists)
        dists = reduce(lambda cumulated, ts: f'{cumulated}\n\t{ts}', ts_as_str)
        return f'Cell type "{self.name}":\n\t{dists}'

    def generate_record(self, transcripts_count):
        sampled_tcs = random.choice(self.__generate_all_transcripts(),
                                    size=transcripts_count,
                                    replace=False)

        def generate_line(line, label):
            return f'{line},{count_nonzero(sampled_tcs == label)}'

        return reduce(generate_line, self.transcript_labels, self.name)

    def __generate_all_transcripts(self):
        def generate_transcripts(cumulated, dist):
            tc_count = random.normal(dist.mean, dist.sd)
            return cumulated + [dist.label] * int(tc_count)

        return reduce(generate_transcripts, self.transcript_dists, [])


def generate_cell_type(type_name, tc_labels, expressed_ratio, dist_range, dist_variance):
    expressed_size = int(len(tc_labels) * expressed_ratio)
    selected = random.choice(tc_labels, expressed_size, replace=False)
    tc_dists = [TranscriptDistribution(label, random.randint(*dist_range), random.randint(*dist_variance))
                for label in selected]
    return CellType(type_name, tc_labels, tc_dists)


def generate_records(records_count, transcripts_count, cell_types):
    for i in range(records_count):
        ctype = random.choice(cell_types)
        yield ctype.generate_record(transcripts_count)
