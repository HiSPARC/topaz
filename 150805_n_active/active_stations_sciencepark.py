import os

from datetime import date
from glob import glob

from numpy import arange, argmax, genfromtxt, histogram, uint32, zeros

from artist import Plot

from sapphire.transformations.clock import datetime_to_gps

PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/5*.tsv'
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]


def read_eventtime(path):
    return genfromtxt(path, delimiter='\t', dtype=uint32, names=['timestamp', 'counts'])


def get_data():
    return {int(os.path.basename(path)[:-4]): read_eventtime(path) for path in glob(PATH)}


def get_aligned():
    data = get_data()

    first = min(data[sn]['timestamp'][0] for sn in STATIONS)
    last = max(data[sn]['timestamp'][-1] for sn in STATIONS)

    timestamps = arange(first, last + 1, 3600)
    extended_data = zeros((len(STATIONS), (last - first) / 3600 + 1))

    for i, sn in enumerate(STATIONS):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        extended_data[i, start:end] = (data[sn]['counts'] > 500) & (data[sn]['counts'] < 5000)
    return timestamps, extended_data


if __name__ == "__main__":
    timestamps, eventtime = get_aligned()
    summed_data = eventtime.sum(axis=0)
    plot = Plot()
    bins = arange(-0.5, len(STATIONS) + 1.5)

    counts, bins = histogram(summed_data, bins=bins)
    counts_in_years = counts / 24.0 / 365.0
    plot.histogram(counts_in_years, bins, linestyle='semitransparent')

    # Exluding data from before 26-09-2008
    start = argmax(timestamps > datetime_to_gps(date(2008, 9, 26)))
    counts, bins = histogram(summed_data[start:], bins=bins)
    counts_in_years = counts / 24.0 / 365.0
    print([(i, sum(counts_in_years[i:])) for i in range(11)])
    plot.histogram(counts_in_years, bins)

    # Exluding data from before 08-03-2010
    start = argmax(timestamps > datetime_to_gps(date(2010, 3, 8)))
    counts, bins = histogram(summed_data[start:], bins=bins)
    counts_in_years = counts / 24.0 / 365.0
    print([(i, sum(counts_in_years[i:])) for i in range(11)])
    plot.histogram(counts_in_years, bins, linestyle='blue')

    # Exluding data from before 01-07-2011
    start = argmax(timestamps > datetime_to_gps(date(2011, 7, 1)))
    counts, bins = histogram(summed_data[start:], bins=bins)
    counts_in_years = counts / 24.0 / 365.0
    print([(i, sum(counts_in_years[i:])) for i in range(11)])
    plot.histogram(counts_in_years, bins, linestyle='red')

    plot.set_ylimits(min=0)
    plot.set_xlimits(min=-0.5, max=len(STATIONS) + 0.5)
    plot.set_ylabel('Number of years')
    plot.set_xlabel('Number of simultaneously active stations (Science Park, sans 507)')
    plot.save_as_pdf('n_stations_spa')
