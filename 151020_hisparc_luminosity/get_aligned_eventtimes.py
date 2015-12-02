from glob import glob
import os
from datetime import date

from artist import Plot
from numpy import genfromtxt, zeros, histogram, arange, where

from sapphire.utils import pbar
from sapphire.transformations.clock import datetime_to_gps


PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/*.csv'


def read_eventtime(path):
    """Read an eventtime csv file"""
    return genfromtxt(path, delimiter='\t', dtype=None,
                      names=['timestamp', 'counts'])


def get_data():
    """Read all eventtime data into a dictionary"""
    return {int(os.path.basename(path)[:-4]): read_eventtime(path)
            for path in pbar(glob(PATH))}


def get_aligned():
    """Get data and align it in an array

    :return: several things are returned:
        - the aligned data filtered for number of events in the hour
        - the aligned data unfiltered
        - first and last timestamp of the array

    """
    data = get_data()

    first = min(values['timestamp'][0] for values in data.values())
    last = max(values['timestamp'][-1] for values in data.values())

    aligned_data = zeros((len(data.keys()), (last - first) / 3600 + 1))
    aligned_data_all = zeros((len(data.keys()), (last - first) / 3600 + 1))

    for i, sn in enumerate(data.keys()):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        aligned_data[i, start:end] = where((data[sn]['counts'] > 500) &
                                           (data[sn]['counts'] < 5000),
                                           data[sn]['counts'], 0)
        aligned_data_all[i, start:end] = data[sn]['counts']
    return aligned_data, aligned_data_all, first, last


if __name__ == "__main__":
    if 'aligned_data_all' not in globals():
        aligned_data, aligned_data_all, first, last = get_aligned()
    n_active_aligned = (aligned_data != 0).sum(axis=0)
    cumsummed_data_all = aligned_data_all.sum(axis=0).cumsum()
    summed_data = aligned_data.sum(axis=0)
    cumsummed_data = summed_data.cumsum()

    timestamp = range(first, last + 1, 3600)
    first_ts = []

    for n in range(aligned_data.shape[0]):
        for ts, has_data in zip(timestamp, aligned_data[n]):
            if has_data:
                first_ts.append(ts)
                break

    first_ts = sorted(first_ts)
    years = range(2004, 2017)

    plot = Plot(width=r'.5\textwidth')
    plot.plot([t / 1e9 for t in first_ts], range(1, len(first_ts) + 1),
              linestyle='black!50!green, thick', mark=None)
    plot.plot([t / 1e9 for t in timestamp[::100]], n_active_aligned[::100],
              linestyle='thick', mark=None)
    plot.set_axis_options('line join=round')
    plot.set_ylabel('Number of stations')
    plot.set_xlabel('Date')
    plot.set_xticks([datetime_to_gps(date(y, 1, 1)) / 1e9 for y in years[::3]])
    plot.set_xtick_labels(['%d' % y for y in years[::3]])
    plot.save_as_pdf('active_stations')

    plot = Plot(width=r'.5\textwidth')
#     plot.plot(timestamp[::100], 1400 * n_active_aligned.cumsum()[::100],
#               linestyle='blue', mark=None)
    plot.plot([t / 1e9 for t in timestamp[::100]], cumsummed_data_all[::100],
              linestyle='black!50!green, thick', mark=None)
    plot.plot([t / 1e9 for t in timestamp[::100]], cumsummed_data[::100],
              linestyle='thick', mark=None)
    plot.set_xticks([datetime_to_gps(date(y, 1, 1)) / 1e9 for y in years[::3]])
    plot.set_xtick_labels(['%d' % y for y in years[::3]])
    plot.set_ylabel('Cummulative number of events')
    plot.set_xlabel('Date')
    plot.save_as_pdf('luminosity_network')
