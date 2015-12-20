"""Check if the offsets remain consistent if calculated via other stations"""

from itertools import combinations, permutations

from numpy import histogram, histogram2d, isnan, array

from artist import Plot

from get_aligned_offsets import get_data


def round_trip(offsets):
    stations = offsets.keys()
    idx = range(len(offsets[stations[0]][stations[1]]))
    for n in [2, 3, 4, 5]:
        plot = Plot()
        ts = []
        offs = []
        for ref in stations:
            for s in combinations(stations, n):
                if ref in s:
                    continue
                offs.extend(offsets[ref][s[0]] +
                            sum(offsets[s[i]][s[i+1]] for i in range(n-1)) +
                            offsets[s[-1]][ref])
                ts.extend(idx)
        ts = array(ts)
        offs = array(offs)
        ts = ts.compress(~isnan(offs))
        offs = offs.compress(~isnan(offs))
        counts, xedges, yedges = histogram2d(ts, offs, bins=(idx[::4], range(-100, 100, 5)))
        plot.histogram2d(counts, xedges, yedges, bitmap=True, type='color')
        plot.set_ylimits(-100, 100)
        plot.set_title('n = %d' % n)
        plot.save_as_pdf('round_trip_%d' % n)


def offset_distribution(offsets):
    stations = offsets.keys()
    for n in [1, 2, 3, 4, 5]:
        plot = Plot()
        offs = []
        for ref in stations:
            for s in permutations(stations, n):
                if ref in s:
                    continue
                offs.extend(offsets[ref][s[0]] +
                            sum(offsets[s[i]][s[i+1]] for i in range(n-1)) +
                            offsets[s[-1]][ref])
        plot.histogram(*histogram(offs, bins=range(-100, 100, 2)))
        plot.set_xlimits(-100, 100)
        plot.set_ylimits(min=0)
        plot.set_title('n = %d' % n)
        plot.save_as_pdf('round_trip_dist_%d' % n)


if __name__ == "__main__":
    offsets = get_data()
    round_trip(offsets)
    offset_distribution(offsets)
