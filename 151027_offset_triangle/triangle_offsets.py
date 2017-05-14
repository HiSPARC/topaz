"""Check if the offsets remain consistent if calculated via other stations"""

from datetime import datetime
from functools import partial
from itertools import combinations, permutations

from numpy import array, histogram, histogram2d, isnan, nanmax, nanmean

from artist import Plot

from sapphire import Station, datetime_to_gps

START = datetime_to_gps(datetime(2011, 6, 1))
STOP = datetime_to_gps(datetime(2016, 2, 1))
STEP = int(86400 * 1)
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]


def get_offsets():
    """Setup nested dictionary with station timing offsets

    The result looks like this:

        {reference1: {station1: func, station2: func}, reference2: {...}, ...}

    Get the offset (and error) between 501-502 on timestamp 1425168000 using:

        offsets[501][502](1425168000)
        # (6.1, 0.72)

    """
    offsets = {ref: {s: partial(Station(s, force_stale=True).station_timing_offset,
                                reference_station=ref)
                     for s in STATIONS if not s == ref}
               for ref in STATIONS}
    return offsets


def get_aligned_offsets(*args, **kwargs):
    """Get dictionary of dictionaries with arrays with offsets"""
    return get_aligned_data(0, *args, **kwargs)


def get_aligned_errors(offsets, start=START, stop=STOP, step=STEP):
    """Get dictionary of dictionaries with arrays with errors"""
    return get_aligned_data(1, *args, **kwargs)


def get_aligned_data(idx, offsets, start=START, stop=STOP, step=STEP):
    """Get dictionary of dictionaries with arrays with offsets or errors"""

    timestamps = range(start, stop, step)
    aoffsets = {ref: {s: array([o(ts)[0] for ts in timestamps])
                      for s, o in stations.iteritems()}
                for ref, stations in offsets.iteritems()}
    return aoffsets


def round_trip(offsets):
    """Examine offset distribution using intermediate stations over time

    Start and end station are the same, but hops via some other stations.
    The result should ideally be an offset of 0 ns.

    :param offsets: Dictionary of dictionaries with offset functions.

    """
    aoffsets = get_aligned_offsets(offsets, START, STOP, STEP)
    timestamps = range(START, STOP, STEP)
    stations = offsets.keys()
    for n in [2, 3, 4, 5]:
        plot = Plot()
        ts = []
        offs = []
        for ref in stations:
            # Intermediate stations
            for s in combinations(stations, n):
                if ref in s:
                    continue
                offs.extend(aoffsets[ref][s[0]] + aoffsets[s[-1]][ref] +
                            sum(aoffsets[s[i]][s[i + 1]] for i in range(n - 1)))
                ts.extend(timestamps)
        ts = array(ts)
        offs = array(offs)
        ts = ts.compress(~isnan(offs))
        offs = offs.compress(~isnan(offs))
        counts, xedges, yedges = histogram2d(ts, offs, bins=(timestamps[::4],
                                                             range(-100, 101, 5)))
        plot.histogram2d(counts, xedges, yedges, bitmap=True, type='color',
                         colormap='viridis')
        plot.set_colorbar()
        plot.set_ylimits(-100, 100)
        plot.set_title('n = %d' % n)
        plot.set_ylabel(r'Station offset residual [\si{\ns}]')
        plot.set_xlabel(r'Timestamp [\si{\s}]')
        plot.save_as_pdf('plots/round_trip_%d' % n)


def offset_distribution(offsets):
    """Examine offset distribution using intermediate stations

    Start and end station are the same, but hops via some other stations.
    The result should ideally be an offset of 0 ns.

    :param offsets: Dictionary of dictionaries with offset functions.

    """
    aoffsets = get_aligned_offsets(offsets, START, STOP, STEP)

    stations = offsets.keys()
    for n in [2, 3, 4, 5]:
        plot = Plot()
        offs = []
        for ref in stations:
            for s in permutations(stations, n):
                if ref in s:
                    continue
                offs.extend(aoffsets[ref][s[0]] + aoffsets[s[-1]][ref] +
                            sum(aoffsets[s[i]][s[i + 1]] for i in range(n - 1)))
        plot.histogram(*histogram(offs, bins=range(-100, 100, 2)))
        plot.set_xlimits(-100, 100)
        plot.set_ylimits(min=0)
        plot.set_title('n = %d' % n)
        plot.set_xlabel(r'Station offset residual [\si{\ns}]')
        plot.save_as_pdf('plots/round_trip_dist_%d' % n)


def stopover(offsets):
    """Compare direct to via offsets for stations far appart

    :param offsets: Dictionary of dictionaries with offset functions.

    """
    aoffsets = get_aligned_offsets(offsets, START, STOP, STEP)
    timestamps = range(START, STOP, STEP)

    stations = offsets.keys()
    for from_station, to_station in combinations(stations, 2):
        plot = Plot()
        all_offs = []

        for i, via_station in enumerate(stations):
            if via_station in [from_station, to_station]:
                continue
            offs = (aoffsets[from_station][via_station] +
                    aoffsets[via_station][to_station])

            all_offs.append(offs)

            plot.plot(timestamps, offs, linestyle='very thin, black!%d' % (i * 5 + 30),
                      mark=None)

        offs = aoffsets[from_station][to_station]
        plot.plot(timestamps, offs, linestyle='red', mark=None)
        # all_offs.append(offs)

        mean_offs = nanmean(all_offs, axis=0)
        plot.plot(timestamps, mean_offs, linestyle='blue', mark=None)

        plot.set_xlimits(START, STOP)
        plot.set_ylimits(-100, 100)
        plot.set_ylabel(r'Station offset residual [\si{\ns}]')
        plot.set_xlabel('Timestamp')
        plot.set_axis_options('line join=round')
        plot.save_as_pdf('plots/stop_over_%d_%d' % (from_station, to_station))


if __name__ == "__main__":
    if 'offsets' not in globals():
        offsets = get_offsets()
#     round_trip(offsets)
#     offset_distribution(offsets)
    stopover(offsets)
