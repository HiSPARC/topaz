"""Check if the offsets remain consistent if calculated via other stations"""

from itertools import combinations, permutations

from get_aligned_offsets import get_data


offsets = get_data()


def round_trip(offsets):
    stations = offsets.keys()
    for n in [1, 2, 3, 4, 5]:
        figure()
        for ref in stations:
            for s in combinations(stations, n):
                if ref in s:
                    continue
                plot(offsets[ref][s[0]] +
                     sum(offsets[s[i]][s[i+1]] for i in range(n-1)) +
                     offsets[s[-1]][ref])
        ylim(-100, 100)
        title('n = %d' % n)


def offset_distribution(offsets):
    stations = offsets.keys()
    idx = range(len(offsets[ref][s[0]])
    for n in [1, 2, 3, 4, 5]:
        ts = []
        offs = []
        figure()
        for ref in stations:
            for s in permutations(stations, n):
                if ref in s:
                    continue
                offs.extend(offsets[ref][s[0]] +
                            sum(offsets[s[i]][s[i+1]] for i in range(n-1)) +
                            offsets[s[-1]][ref])
                ts.extend(idx)
        hist(offs, bins=range(-100, 100, 2))
        xlim(-100, 100)
        title('n = %d' % n)


if __name__ == "__main__":
    offsets = get_data()
    round_trip(offets)
    offset_distribution(offsets)
