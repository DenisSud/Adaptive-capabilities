import csv
from itertools import tee, zip_longest
import numpy as np
import os

def detect_dips(data):
    diff = [data[i + 1] - data[i] for i in range(len(data) - 1)]
    dips = [d for d, e in zip_longest(diff, diff[1:], fillvalue=float('inf')) if d < 0 and e > 0]
    return dips[dips > -0.1] if len(dips) > 0 else None

def load_csv_column(file_path, column_index):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(float(row[column_index]))
    return np.array(data)


def main():
    # TODO
    pass
if __name__ == "__main__":
    main()