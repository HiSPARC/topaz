from datetime import date

from numpy import max as npmax
from numpy import argsort, array, average, where, zeros
from scipy.stats import binned_statistic

from artist import Plot

from sapphire import Network, Station
from sapphire.transformations.clock import datetime_to_gps
from sapphire.utils import pbar

YEARS = range(2004, 2017)
SPA_STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]


def get_eventtime_data(station):
    """Get eventtime data"""
    return Station(station, force_stale=True).event_time()


def get_station_numbers():
    """Get all station numbers"""
    return Network(force_stale=True).station_numbers()


def get_data():
    """Read all eventtime data into a dictionary"""
    return {s: get_eventtime_data(s) for s in pbar(get_station_numbers())}


def get_station_end_timestamp(station, data):
    """Read all eventtime data into a dictionary"""

    if Station(station, force_stale=True).info['active']:
        return None
    else:
        # Start of day after last day with data
        return data[station]['timestamp'][-1] + 3600


def get_aligned(data):
    """Get data and align it in an array

    Data from a station is on a row, the columns are the hourly bins.

    :return: several things are returned:
        - the aligned data filtered for number of events in the hour
        - the aligned data unfiltered
        - first and last timestamp of the array

    """
    first = min(values['timestamp'][0] for values in data.values())
    last = max(values['timestamp'][-1] for values in data.values())

    aligned_data = zeros((len(data.keys()), (last - first) / 3600 + 1))
    aligned_data_all = zeros((len(data.keys()), (last - first) / 3600 + 1))

    for i, sn in enumerate(sorted(data.keys())):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        aligned_data[i, start:end] = where((data[sn]['counts'] > 500) &
                                           (data[sn]['counts'] < 5000),
                                           data[sn]['counts'], 0)
        aligned_data_all[i, start:end] = data[sn]['counts']
    return aligned_data, aligned_data_all, first, last


def plot_luminosity(timestamp, aligned_data, aligned_data_all, i):

    n_active_aligned = (aligned_data != 0).sum(axis=0)
    cumsummed_data_all = aligned_data_all.sum(axis=0).cumsum()
    summed_data = aligned_data.sum(axis=0)
    cumsummed_data = summed_data.cumsum()

    plot = Plot(width=r'.5\textwidth')
#     plot.plot([t / 1e9 for t in timestamp[::100]], cumsummed_data_all[::100],
#               linestyle='black!50!green, thick', mark=None)
    plot.plot([t / 1e9 for t in timestamp[::100]], cumsummed_data[::100],
              linestyle='thick', mark=None)
    plot.set_xticks([datetime_to_gps(date(y, 1, 1)) / 1e9 for y in YEARS[::3]])
    plot.set_xtick_labels(['%d' % y for y in YEARS[::3]])
    plot.set_ylabel('Cummulative number of events')
    plot.set_xlabel('Date')
    plot.save_as_pdf('luminosity_%s' % ['network', 'spa'][i])


def plot_active_stations(timestamps, stations, aligned_data, data, i):

    first_ts = []
    last_ts = []
    stations_with_data = []

    assert aligned_data.shape[0] == len(stations)

    for n in range(aligned_data.shape[0]):
        prev_ts = 0
        for ts, has_data in zip(timestamps, aligned_data[n]):
            if has_data:
                if prev_ts > 30:
                    # Running for at least 30 hours.
                    first_ts.append(ts)
                    stations_with_data.append(stations[n])
                    break
                else:
                    prev_ts += 1
            else:
                prev_ts = 0

    for station in stations_with_data:
        end_ts = get_station_end_timestamp(station, data)
        if end_ts is not None:
            last_ts.append(end_ts)

    first_ts = sorted(first_ts)
    last_ts = sorted(last_ts)
    diff_stations = array([1] * len(first_ts) + [-1] * len(last_ts))
    idx = argsort(first_ts + last_ts)
    n_stations = diff_stations[idx].cumsum()

    # Get maximinum number of simultaneaously active stations per 7 days
    n_active_aligned = (aligned_data != 0).sum(axis=0)
    n_binned, t_binned, _ = binned_statistic(timestamps, n_active_aligned,
                                             npmax,
                                             bins=len(timestamps) / (7 * 24))
    # Get average number of detected events per 7 days
    # todo; scale 2/4 detector stations
    summed_data = aligned_data.sum(axis=0)
    e_binned, t_binned, _ = binned_statistic(timestamps, summed_data,
                                             average,
                                             bins=len(timestamps) / (7 * 24))

    plot = Plot(width=r'.5\textwidth')
    plot.plot([t / 1e9 for t in sorted(first_ts + last_ts)], n_stations,
              linestyle='gray, thick', mark=None, use_steps=True)
    plot.histogram(n_binned, t_binned / 1e9, linestyle='thick')
    plot.histogram(e_binned * max(n_binned) / max(e_binned), t_binned / 1e9,
                   linestyle='blue')
    plot.set_axis_options('line join=round')
    plot.set_ylabel('Number of stations')
    plot.set_xlabel('Date')
    plot.set_ylimits(min=0)
    plot.set_xticks([datetime_to_gps(date(y, 1, 1)) / 1e9 for y in YEARS[::3]])
    plot.set_xtick_labels(['%d' % y for y in YEARS[::3]])
    plot.save_as_pdf('active_stations_%s' % ['network', 'spa'][i])


if __name__ == "__main__":
    if 'data' not in globals():
        data = get_data()
        data_spa = {s: data[s] for s in SPA_STATIONS}

    for i, d in enumerate([data, data_spa]):
        stations = sorted(d.keys())
        aligned_data, aligned_data_all, first, last = get_aligned(d)
        timestamp = range(first, last + 1, 3600)
        plot_active_stations(timestamp, stations, aligned_data, d, i)
        plot_luminosity(timestamp, aligned_data, aligned_data_all, i)
