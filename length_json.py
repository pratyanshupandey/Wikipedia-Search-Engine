import json


def load_legth(path):
    file = open(path, 'rw+')
    lengths = []

    json.dump({"lengths": lengths}, file)

convert("prev_data/lengths")