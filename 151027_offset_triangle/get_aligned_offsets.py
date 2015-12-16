from glob import glob
import os

from artist import Plot
from numpy import genfromtxt, zeros, histogram, arange, where, nan
from sapphire.utils import pbar


PATH = '/Users/arne/Datastore/station_offsets/offsets_ref{ref}_s{s}.tsv'
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510]


def read_offsets(path):
    return genfromtxt(path, delimiter='\t', dtype=None, names=['timestamp', 'offsets'])


# def align_data(off):
#     first = 1262304000 # min(values['timestamp'][0] for values in data.values())
#     last = 1425168000 # max(values['timestamp'][-1] for values in data.values())
#     period = 2419200
#
#     aligned_offsets = zeros((last - first) / period + 1)
#     start = (off['timestamp'][0] - first) / period
#     end = start + len(off)
#     aligned_offsets[start:end] = off['offsets']
#     aligned_offsets = where(aligned_offsets == 0, nan, aligned_offsets)
#     return aligned_offsets


def get_data():
    offsets = {ref: dict.fromkeys(STATIONS) for ref in STATIONS}
    for ref in STATIONS:
        for s in STATIONS:
            if ref == s:
                continue
            off = read_offsets(PATH.format(ref=ref, s=s))
            offsets[ref][s] = off['offsets']
    return offsets


if __name__ == "__main__":
    offsets = get_data()
