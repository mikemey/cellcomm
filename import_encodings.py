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
encodings_dir = f'{run_id}/logs/encodings'


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
        encoding = {
            '_id': iteration_,
            'points': self.__convert_coords(coords_)
        }
        self.encodings_coll.insert_one(encoding)

    def __convert_coords(self, coords_):
        points = []
        for i, (point, barcode) in enumerate(zip(coords_, self.barcodes)):
            points.append({
                'id': i + 1,
                'n': barcode,
                'x': point[0].item(),
                'y': point[1].item(),
                'z': point[2].item()
            })
        return points


if __name__ == '__main__':
    encoding_files = os.listdir(encodings_dir)
    iterations = [enc_file.rstrip('.enc') for enc_file in encoding_files]
    size = len(iterations)
    importer = DBImporter()

    for ix, iteration in enumerate(iterations):
        enc_num = ix + 1
        print(f'\rprocessing encoding {enc_num}/{size}: load... ', end='')
        coords = load_coords(iteration)
        print(f'import... ', end='')
        importer.insert_coords(iteration, coords)
        if enc_num < size:
            print('\r', ' ' * 80, end='')
    print('\nDONE')
