from numpy import mean
import warnings

from sapphire import HiSPARCStations

from station_distances import close_pairs_in_network


def variable_distance_pairs(pairs):
    variable_pairs = [min_max_distance_pair(pair) for pair in pairs]
    return variable_pairs


def min_max_distance_pair(pair):
    """Calculate station distance for all timestamps

    For each timestamp (GPS and station layout) calculate the station
    distances.

    """
    c = HiSPARCStations(pair, force_stale=True)
    ts = list(c.stations[0].timestamps)
    ts += list(c.stations[1].timestamps)
    ts += list(c.stations[0].detectors[0].timestamps)
    ts += list(c.stations[1].detectors[0].timestamps)
    distances = []
    for t in sorted(ts):
        c.set_timestamp(t)
        distances.append(c.calc_distance_between_stations(*pair))
    return (min(distances), max(distances))


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        pairs = close_pairs_in_network(min=30, max=15e3)
        variable_pairs = variable_distance_pairs(pairs)
