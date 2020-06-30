import os
from functools import reduce
from typing import List

import sys
from numpy import random, count_nonzero

MAX_TRANSCRIPTS = pow(26, 3)


def generate_feature_labels(label_count):
    if label_count > MAX_TRANSCRIPTS:
        raise AssertionError(f'too many transcripts: {label_count}')
    tcs = []
    char_range = range(65, 91)
    for i in char_range:
        for j in char_range:
            for k in char_range:
                tcs.append(f'{i:c}{j:c}{k:c}')
                if len(tcs) == label_count:
                    return tcs


class FeatureDistribution:
    def __init__(self, label, mean, sd):
        self.label = label
        self.mean = mean
        self.sd = sd

    def __str__(self):
        return f'Feature "{self.label}" mean: {self.mean}, std-dev: {self.sd}'


class CellType:
    def __init__(self, name, feat_labels, t_dists: List[FeatureDistribution]):
        self.name = name
        self.feature_labels = feat_labels
        self.feature_dists = t_dists

    def __str__(self):
        ts_as_str = map(str, self.feature_dists)
        dists = reduce(lambda cumulated, ts: f'{cumulated}\n\t{ts}', ts_as_str)
        return f'Cell type "{self.name}":\n\t{dists}'

    def generate_csv_record(self, transcripts_count):
        sampled_tcs = random.choice(self.__generate_all_transcripts(),
                                    size=transcripts_count,
                                    replace=False)
        result = [self.name]
        for label in self.feature_labels:
            result.append(str(count_nonzero(sampled_tcs == label)))
        return ','.join(result) + '\n'

    def __generate_all_transcripts(self):
        result = []
        for dist in self.feature_dists:
            tc_count = random.normal(dist.mean, dist.sd)
            result.extend([dist.label] * int(tc_count))
        return result


def generate_cell_type(type_name, feat_labels, expressed_ratio, dist_range, dist_variance):
    expressed_size = int(len(feat_labels) * expressed_ratio)
    selected = random.choice(feat_labels, expressed_size, replace=False)
    tc_dists = [FeatureDistribution(label, random.randint(*dist_range), random.randint(*dist_variance))
                for label in selected]
    return CellType(type_name, feat_labels, tc_dists)


def generate_csv_header(labels):
    return 'cell_type,' + ','.join(labels) + '\n'


def generate_csv_records(records_count, transcripts_count, cell_types):
    for i in range(records_count):
        print(f'generate {i + 1} / {records_count}', end='\r', flush=True)
        cell_type = random.choice(cell_types)
        yield cell_type.generate_csv_record(transcripts_count)
    print()


def generate_to_file(file_name,
                     records_count=10000,
                     total_feature_count=10000,
                     max_reads_per_cell=3000):
    feature_labels = generate_feature_labels(total_feature_count)
    records = generate_csv_records(
        records_count=records_count,
        transcripts_count=max_reads_per_cell,
        cell_types=[
            generate_cell_type('c01', feature_labels, 0.4, (10, 1000), (10, 500)),
            generate_cell_type('c02', feature_labels, 0.45, (120, 2000), (50, 500)),
            generate_cell_type('c03', feature_labels, 0.35, (30, 4000), (20, 500)),
            generate_cell_type('c04', feature_labels, 0.5, (10, 3000), (10, 500)),
            generate_cell_type('c05', feature_labels, 0.55, (220, 1000), (100, 500)),
            generate_cell_type('c06', feature_labels, 0.5, (20, 2000), (200, 500)),
            generate_cell_type('c07', feature_labels, 0.4, (150, 3000), (100, 500)),
            generate_cell_type('c08', feature_labels, 0.25, (120, 3500), (480, 700)),
            generate_cell_type('c09', feature_labels, 0.3, (60, 2500), (350, 500)),
            generate_cell_type('c11', feature_labels, 0.33, (320, 4800), (320, 500)),
            generate_cell_type('c12', feature_labels, 0.39, (80, 5500), (120, 320)),
            generate_cell_type('c13', feature_labels, 0.41, (140, 3200), (20, 600)),
            generate_cell_type('c14', feature_labels, 0.20, (10, 1500), (220, 500)),
            generate_cell_type('c15', feature_labels, 0.15, (5, 2200), (70, 350)),
            generate_cell_type('c16', feature_labels, 0.6, (200, 3500), (50, 450))
        ])

    print('generate/write records:')
    with open(file_name, 'a') as f:
        f.write(generate_csv_header(feature_labels))
        f.writelines(records)
    print('DONE')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('ERROR: file path required')
        exit(-1)

    data_file = sys.argv[1]
    if os.path.exists(data_file):
        print(f'ERROR: file exists already: {data_file}')
        exit(-2)

    generate_to_file(data_file)
