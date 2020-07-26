#!/usr/bin/env python3
import os
import pickle

import numpy as np
import sys
from pymongo import MongoClient
from pymongo.collection import Collection

if len(sys.argv) < 3:
    name = os.path.basename(__file__)
    print(f'\nrequired parameters missing: ./{name} <run-id> <barcode-file>')
    exit(-1)

MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'cellcomm'
MONGO_COLLECTION = 'encs'

run_id = sys.argv[1]
barcode_file = sys.argv[2]
encodings_dir = f'logs/{run_id}/encodings'


def load_coords(iteration_):
    with open(f'{encodings_dir}/{iteration_}.enc', 'rb') as f:
        encodings = pickle.load(f)
        return np.multiply(encodings, 255)


def load_barcodes():
    result = []
    with open(barcode_file) as f:
        for line in f.readlines():
            result.append(line.strip())
    return result


class DBImporter:
    def __init__(self):
        client = MongoClient(MONGO_URL)
        self.encodings_coll: Collection = client[MONGO_DB][MONGO_COLLECTION]
        self.barcodes = load_barcodes()

    def insert_coords(self, iteration_, coords_):
        ids, names = self.__create_point_meta(coords_)
        encoding = {
            '_id': iteration_,
            'pids': ids,
            'ns': names,
            'xs': coords_[:, 0].tolist(),
            'ys': coords_[:, 1].tolist(),
            'zs': coords_[:, 2].tolist()
        }
        self.encodings_coll.insert_one(encoding)

    def __create_point_meta(self, coords_):
        if len(self.barcodes) != len(coords_):
            raise ValueError(f'Coordinates-/barcode-data different length: {len(self.barcodes)} != {len(coords_)}')
        point_ids, point_names = [], []
        for i, barcode in enumerate(self.barcodes):
            point_ids.append(i + 1)
            point_names.append(barcode)
        return point_ids, point_names


if __name__ == '__main__':
    encoding_files = os.listdir(encodings_dir)
    iterations = [enc_file.rstrip('.enc') for enc_file in encoding_files]
    size = len(iterations)
    importer = DBImporter()

    for ix, iteration in enumerate(iterations):
        enc_num = ix + 1
        print(f'\rprocessing encoding {enc_num}/{size}... ', end='')
        coords = load_coords(iteration)
        importer.insert_coords(iteration, coords)
    print('\nDONE')
