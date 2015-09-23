from glob import glob
import os

from artist import Plot
from numpy import genfromtxt, zeros, histogram, arange


PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/5*.csv'
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]


def read_eventtime(path):
    return genfromtxt(path, delimiter='\t', dtype=None, names=['timestamp', 'counts'])


def get_data():
    return {int(os.path.basename(path)[:-4]): read_eventtime(path)
            for path in glob(PATH)}

def get_aligned():
    data = get_data()

    first = min(data[sn]['timestamp'][0] for sn in STATIONS)
    last = max(data[sn]['timestamp'][-1] for sn in STATIONS)

    extended_data = zeros((len(STATIONS), (last - first) / 3600 + 1))

    for i, sn in enumerate(STATIONS):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        extended_data[i, start:end] = (data[sn]['counts'] > 500) & (data[sn]['counts'] < 5000)
    return extended_data


if __name__ == "__main__":
    eventtime = get_aligned()
    summed_data = eventtime.sum(axis=0)
    plot = Plot()

    counts, bins = histogram(summed_data, bins=arange(-.5, len(STATIONS) + 1.5))
    counts_in_years = counts / 24. / 365.
    plot.histogram(counts_in_years, bins, linestyle='semitransparent')

    # Exluding data from before 26-09-2008
    counts, bins = histogram(summed_data[39500:], bins=arange(-.5, len(STATIONS) + 1.5))
    counts_in_years = counts / 24. / 365.
    print [(i, sum(counts_in_years[i:])) for i in range(11)]
    plot.histogram(counts_in_years, bins)

    plot.set_ylimits(min=0)
    plot.set_xlimits(min=-0.5, max=len(STATIONS) + .5)
    plot.set_ylabel('Number of years')
    plot.set_xlabel('Number of simultaneously active stations (Science Park, sans 507)')
    plot.save_as_pdf('n_stations')
