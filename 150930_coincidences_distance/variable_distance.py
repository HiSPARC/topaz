import warnings

from numpy import mean

from artist import Plot

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


def plot_min_max(variable_pairs):
    plot = Plot()
    variable_pairs = sorted(variable_pairs)
    for i, minmax_d in enumerate(variable_pairs):
        plot.plot([i, i], minmax_d, mark=None)
    plot.set_xlabel('Station pair')
    plot.set_xtick_labels([' '])
    plot.set_ylabel(r'Distance between stations [\si{\meter}]')
    plot.save_as_pdf('min_max_distances')


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        pairs = close_pairs_in_network(min=30, max=15e3)
        variable_pairs = variable_distance_pairs(pairs)
    plot_min_max(variable_pairs)
