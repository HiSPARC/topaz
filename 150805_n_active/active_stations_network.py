import os

from datetime import date
from glob import glob

from numpy import arange, argmax, genfromtxt, histogram, uint32, zeros

from artist import Plot

from sapphire.transformations.clock import datetime_to_gps

PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/*.tsv'


def read_eventtime(path):
    return genfromtxt(path, delimiter='\t', dtype=uint32,
                      names=['timestamp', 'counts'])


def get_data():
    return {int(os.path.basename(path)[:-4]): read_eventtime(path)
            for path in glob(PATH)}


def get_aligned():
    data = get_data()

    first = min(values['timestamp'][0] for values in data.values())
    last = max(values['timestamp'][-1] for values in data.values())

    timestamps = arange(first, last + 1, 3600)
    extended_data = zeros((len(data.keys()), (last - first) / 3600 + 1))

    for i, sn in enumerate(data.keys()):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        extended_data[i, start:end] = ((data[sn]['counts'] > 500) &
                                       (data[sn]['counts'] < 5000))
    return timestamps, extended_data


if __name__ == "__main__":
    timestamps, eventtime = get_aligned()
    summed_data = eventtime.sum(axis=0)
    plot = Plot()

    counts, bins = histogram(summed_data, bins=arange(-.5, 100.5, 1))
    counts_in_years = counts / 24. / 365.
    plot.histogram(counts_in_years, bins)

    # Exluding data from before 08-03-2010
    start = argmax(timestamps > datetime_to_gps(date(2010, 3, 8)))
    counts, bins = histogram(summed_data[start:], bins=bins)
    counts_in_years = counts / 24. / 365.
    plot.histogram(counts_in_years, bins, linestyle='blue')

    # Exluding data from before 01-07-2011
    start = argmax(timestamps > datetime_to_gps(date(2011, 7, 1)))
    counts, bins = histogram(summed_data[start:], bins=bins)
    counts_in_years = counts / 24. / 365.
    plot.histogram(counts_in_years, bins, linestyle='red')

    plot.set_ylimits(min=0)
    plot.set_xlimits(min=-0.5, max=100.5)
    plot.set_ylabel('Number of years')
    plot.set_xlabel('Number of simultaneously active stations')
    plot.save_as_pdf('n_stations_network')
