# attention: works only for 3-digit PheCodes
PHE_CODES = ['394', '395', '396', '401.2', '411.1', '411.2', '411.3', '411.4', '411.9', '411.8', '414', '415', '420',
             '420.1', '420.3', '420.2', '425', '425.1', '425.2', '426', '426.2', '426.3', '426.4', '426.8', '427.1',
             '427.2', '427.3', '427.41', '427.42', '427.5', '427.6', '427.7', '428.1', '428.2', '429.1', '656.9', '747']
DATA_PATH = 'data/raw_assoc'

from os import listdir, path


def read_files():
    for file in filter(lambda file_name: file_name.startswith('ICD_'), listdir(DATA_PATH)):
        file_path = path.join(DATA_PATH, file)
        try:
            with open(file_path) as f:
                f.readline()
                f.readline()
                for line in f.readlines():
                    cells = line.split('\t')
                    if cells[0] in PHE_CODES:
                        yield line
        except Exception as e:
            print(file_path)
            print(e)
            exit(-1)


if __name__ == '__main__':
    with open('hla_hd_assoc.txt', 'w+') as out_file:
        for rel_line in read_files():
            out_file.write(rel_line)
