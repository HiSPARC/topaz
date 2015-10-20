from glob import glob
import os

from artist import Plot
from numpy import genfromtxt, zeros, histogram, arange, where
from sapphire.utils import pbar


PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/*.csv'


def read_eventtime(path):
    return genfromtxt(path, delimiter='\t', dtype=None, names=['timestamp', 'counts'])


def get_data():
    return {int(os.path.basename(path)[:-4]): read_eventtime(path)
            for path in pbar(glob(PATH))}


def get_aligned():
    data = get_data()

    first = min(values['timestamp'][0] for values in data.values())
    last = max(values['timestamp'][-1] for values in data.values())

    aligned_data = zeros((len(data.keys()), (last - first) / 3600 + 1))

    for i, sn in enumerate(data.keys()):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        aligned_data[i, start:end] = where((data[sn]['counts'] > 500) &
                                           (data[sn]['counts'] < 5000),
                                           data[sn]['counts'], 0)
    return aligned_data, first, last


if __name__ == "__main__":
    aligned_data, first, last = get_aligned()
    summed_data = aligned_data.sum(axis=0)
    cumsummed_data = summed_data.cumsum()
    plot = Plot()
    timestamp = range(first, last + 1, 3600)

    plot.plot(timestamp[::100], cumsummed_data[::100], mark=None)

    plot.set_ylabel('Cummulative number of events')
    plot.set_xlabel('Date')
    plot.save_as_pdf('luminosity_network')
