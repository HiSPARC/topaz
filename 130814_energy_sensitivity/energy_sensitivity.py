"""Energy sensitivity Science Park

Calculate the energy sensitivity of stations and clusters. Set the desired
minimum number of detectors that need to have been hit in each station and the
required number of stations.

For each point on the map a bisection (of shower energies) will be performed
which will calculate the detection probability using Poisson probability. It
will try to approach the requested detection_probability.

Each combination is considered when determining the probability.

"""

import os

from functools import partial
from itertools import combinations, product
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Ellipse

from artist import Plot

from sapphire import HiSPARCStations, ScienceParkCluster
from sapphire.clusters import BaseCluster, SingleDiamondStation, SingleStation, SingleTwoDetectorStation
from sapphire.simulations.ldf import KascadeLdf
from sapphire.utils import pbar


def multi_find_min_energy(cls, xy):
    return cls.find_min_energy(xy[0], xy[1])


class EnergySensitivity(object):

    def __init__(self):
        # Detectors
        stations = [501, 503, 506]
        self.cluster = ScienceParkCluster(stations=stations)

        # Conditions
        self.detection_probability = 0.5
        self.min_detectors = 2
        self.min_stations = 3

        # Shower parameters
        self.ldf = KascadeLdf()
        self.grid_points = 2500
        self.max_radius = 1000
        self.min_energy = 1e12
        self.max_energy = 1e21
        self.start_energy = 1e17
        self.bisections = 11

        # Throw showers in a regular grid around center mass of the station
        xc, yc, _ = self.cluster.calc_center_of_mass_coordinates()
        self.xx = np.linspace(-self.max_radius + xc, self.max_radius + xc,
                              np.sqrt(self.grid_points))
        self.yy = np.linspace(-self.max_radius + yc, self.max_radius + yc,
                              np.sqrt(self.grid_points))

    def main(self):
        # Cache detector positions
        for station in self.cluster.stations:
            for detector in station.detectors:
                detector.xy_coordinates = detector.get_xy_coordinates()
        # Results
        self.results = self.get_min_energy_per_bin()

    def show_restults(self):
        self.plot_scintillators_in_cluster()
        self.plot_energy_acceptance()
#         self.draw_background_map()

    def get_area_energy(self, energy):
        n_bins = np.sum(self.results < energy)
        bin_area = abs((self.xx[1] - self.xx[0]) * (self.yy[1] - self.yy[0]))
        area = n_bins * bin_area

        return area

    def get_min_energy_per_bin(self):

        worker_pool = Pool()
        temp_multi_find_min_energy = partial(multi_find_min_energy, self)
        results = worker_pool.map(temp_multi_find_min_energy,
                                  product(self.xx, self.yy))
        worker_pool.close()
        worker_pool.join()
#         results = [temp_multi_find_min_energy(xy) for xy in product(self.xx, self.yy)]
        results = np.array(results).reshape((len(self.xx), len(self.yy))).T

        return results

    def find_min_energy(self, xc, yc):
        # Use bisection to quickly get the final energy
        energy = self.start_energy
        lo = self.min_energy
        hi = self.max_energy
        for _ in range(self.bisections):
            n_electrons = 10 ** (np.log10(energy) - 15 + 4.8)
            station_densities = self.calculate_densities_for_cluster(xc, yc, n_electrons)
            p_cluster = self.detection_probability_for_cluster(station_densities)
            if p_cluster == self.detection_probability:
                break
            elif p_cluster < self.detection_probability:
                lo = energy
            else:
                hi = energy
            energy = 10 ** ((np.log10(lo) + np.log10(hi)) / 2.0)

        return energy

    def detection_probability_for_cluster(self, station_densities):
        """Determine the probability of 'coincidence'

        Calculate the probability of the requested coincidence using
        statistics. Fist the probability of a good detection in each station
        is determined. Then it looks for the probability that at least a given
        number of stations detects the shower.

        :param station_densities: list of densities at each detectors in
                                  each of the stations.
        :return: probability of a coicidence.

        """
        if len(station_densities) < self.min_stations:
            # To few stations
            return 0

        p_stations = [self.detection_probability_for_station(detector_densities)
                      for detector_densities in station_densities]
        p0_stations = [1. - p for p in p_stations]
        p_cluster = self.calculate_p(p_stations, p0_stations,
                                     self.min_stations)

        return p_cluster

    def detection_probability_for_station(self, detector_densities):
        """Determine the probability of 'trigger'

        Calculate the probability of the requested detection using Poisson
        statistics. Each detector will be marked as hit when it has at least
        one particle. At least `min_detectors` need to be hit to count towards
        the probability of a good detection.

        :param detector_densities: list of densities at each detectors in
                                  the station.
        :return: list of probabilities for each station.

        """
        if len(detector_densities) < self.min_detectors:
            # To few detectors
            return 0

        p0_detectors = [self.p0(density) for density in detector_densities]
        p_detectors = [1. - p0 for p0 in p0_detectors]
        p_station = self.calculate_p(p_detectors, p0_detectors,
                                     self.min_detectors)
        return p_station

    def calculate_p(self, p, p0, min_n):
        n_p = len(p)
        p_total = 0
        for n in range(min_n, n_p + 1):
            for i in combinations(range(n_p), n):
                p_combination = 1.
                for j in range(n_p):
                    if j in i:
                        # Probability of trigger
                        p_combination *= p[j]
                    else:
                        # Probability of no trigger
                        p_combination *= p0[j]
                p_total += p_combination

        return p_total

    def p(self, detector_density):
        """Chance of at least one particle in detector"""

        return 1.0 - self.p0(detector_density)

    def p0(self, detector_density):
        """Chance of detecting no particle in a detector"""

        return np.exp(-detector_density / 2.)

    def calculate_densities_for_cluster(self, x, y, n_electrons):
        densities = [self.calculate_densities_for_station(station, x, y, n_electrons)
                     for station in self.cluster.stations]

        return densities

    def calculate_densities_for_station(self, station, x, y, n_electrons):
        densities = [self.calculate_densities_for_detector(detector, x, y, n_electrons)
                     for detector in station.detectors]

        return densities

    def calculate_densities_for_detector(self, detector, x, y, n_electrons):
        r = self.calculate_detector_core_distance(detector, x, y)
        density = self.ldf.calculate_ldf_value(r, n_electrons)

        return density

    def calculate_detector_core_distance(self, detector, x, y):
        x0, y0 = detector.xy_coordinates
        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)

        return r

    def plot_scintillators_in_cluster(self):
        # Draw station locations on a map
        for station in self.cluster.stations:
            for detector in station.detectors:
                detector_x, detector_y = detector.get_xy_coordinates()
                plt.scatter(detector_x, detector_y, marker=',', c='r',
                            edgecolor='none', s=6)
            station_x, station_y, station_a = station.get_xyalpha_coordinates()
            plt.scatter(station_x, station_y, marker=',', c='b',
                        edgecolor='none', s=3)

    def plot_energy_acceptance(self):
        # Grid
        min_energy = np.log10(self.min_energy)
        max_energy = np.log10(self.max_energy)
        levels = (max_energy - min_energy) * 3 + 1
        label_levels = (max_energy - min_energy) + 1
        contour = plt.contour(self.xx, self.yy, self.results,
                              np.logspace(min_energy, max_energy, levels))
        plt.clabel(contour, np.logspace(min_energy, max_energy, label_levels),
                   inline=1, fontsize=8, fmt='%.0e')

    def draw_background_map(self):
        self_path = os.path.dirname(__file__)
        map_path = os.path.join(self_path, "backgrounds/ScienceParkMap_1.092.png")

        # Draw Science Park Map on 1:1 scale (1 meter = 1 pixel)
        background = plt.imread(map_path)
        # determine pixel:meter ratio for different OSM zoom levels at Science Park..
        bg_scale = 1.092
        bg_width = background.shape[1] * bg_scale
        bg_height = background.shape[0] * bg_scale
        plt.imshow(background, aspect='equal', alpha=0.5,
                   extent=[-bg_width, bg_width, -bg_height, bg_height])


class SingleStationSensitivity(EnergySensitivity):

    def __init__(self):
        super(SingleStationSensitivity, self).__init__()

        # Detectors
        self.cluster = SingleStation()

        # Conditions
        self.min_stations = 1


class SingleTwoEnergySensitivity(SingleStationSensitivity):

    def __init__(self):
        super(SingleTwoEnergySensitivity, self).__init__()

        # Detectors
        self.cluster = SingleTwoDetectorStation()


class SingleDiamondEnergySensitivity(SingleStationSensitivity):

    def __init__(self):
        super(SingleDiamondEnergySensitivity, self).__init__()

        # Detectors
        self.cluster = SingleDiamondStation()


class StationPairEnergySensitivity(EnergySensitivity):

    def __init__(self, pair):
        super(StationPairEnergySensitivity, self).__init__()

        # Detectors
        self.cluster = HiSPARCStations(pair)

        # Conditions
        self.min_stations = 2


class StationPairEnergySensitivityQuarter(EnergySensitivity):

    """Subclass to only consider one quarter

    This only works if the cluster is (almost) symmetric.
    So either two 2-detector stations, or two 4-detector stations.

    """

    def __init__(self, pair):
        super(StationPairEnergySensitivityQuarter, self).__init__()

        # Detectors
        self.cluster = HiSPARCStations(pair, force_stale=True)

        # Conditions
        self.min_stations = 2

        # Shower parameters
        self.max_radius = 1e3
        self.bin_size = 10.
#         self.max_radius = bin_size * np.sqrt(self.grid_points)

        # Throw showers in one grid around center mass of the stations
#         xc, yc, _ = self.cluster.calc_center_of_mass_coordinates()
#         self.xx = np.arange(-self.max_radius + xc, self.max_radius + xc, self.bin_size)
#         self.yy = np.arange(-self.max_radius + yc, self.max_radius + yc, self.bin_size)

        # Rotate cluster to make stations aligned along x for easy symmetry
        _, phi, _ = self.cluster.calc_rphiz_for_stations(0, 1)
        self.cluster.alpha = -phi

        # Throw showers in one quarter from center mass of the stations
        xc, yc, _ = self.cluster.calc_center_of_mass_coordinates()
        self.xx = np.arange(xc + self.bin_size / 2., self.max_radius + xc, self.bin_size)
        self.yy = np.arange(yc + self.bin_size / 2., self.max_radius + yc, self.bin_size)

    def get_area_energy(self, energy):
        """Calculate area

        Multiply area by four, because only one quadrant was considered.

        """
        area = super(StationPairEnergySensitivity, self).get_area_energy(energy)
        area *= 4.

        return area


class StationPairAreaEnergySensitivity(StationPairEnergySensitivity):

    """Subclass to only consider axis between stations and parallel

    This only works if the cluster is (almost) symmetric.
    So either two 2-detector stations, or two 4-detector stations.
    This assumes that the resulting iso-sensitivity lines are ellipse-like.

    """

    def __init__(self, pair):
        super(StationPairAreaEnergySensitivity, self).__init__(pair)

        # Shower parameters
        self.max_radius = 25e3
        self.step_size = 2.

        # Rotate cluster to make stations aligned along x for easy symmetry
        _, phi, _ = self.cluster.calc_rphiz_for_stations(0, 1)
        self.cluster.alpha = -phi

        # Throw showers along axis between stations and parallel at point
        # between the stations
        xc, yc, _ = self.cluster.calc_center_of_mass_coordinates()
        self.xx = np.arange(xc, self.max_radius + xc, self.step_size)
        self.yy = np.arange(yc, self.max_radius + yc, self.step_size)

    def get_area_energy(self, energy):
        """Calculate area

        Assume iso-sensitivity lines make ellipses with x and y as semi-major
        and semi-minor axes.

        """
        a = np.interp(energy, self.results[0], self.xx) - self.xx[0]
        b = np.interp(energy, self.results[1], self.yy) - self.yy[0]
        area = np.pi * a * b

        return area

    def get_min_energy_per_bin(self):
        """Only calculate along x, y axes with center between stations"""

        temp_multi_find_min_energy = partial(multi_find_min_energy, self)
        worker_pool = Pool()
        x_results = np.array(worker_pool.map(temp_multi_find_min_energy,
                                             [(x, self.yy[0]) for x in self.xx], chunksize=10))
        y_results = np.array(worker_pool.map(temp_multi_find_min_energy,
                                             [(self.xx[0], y) for y in self.yy], chunksize=10))
        worker_pool.close()
        worker_pool.join()
#         x_results = np.array([temp_multi_find_min_energy(xy) for xy in
#                               [(x, self.yy[0]) for x in self.xx]])
#         y_results = np.array([temp_multi_find_min_energy(xy) for xy in
#                               [(self.xx[0], y) for y in self.yy]])

        return (x_results, y_results)

    def plot_energy_acceptance(self):
        """Plot itnerpolated ellipses instead of contours"""

        # Grid
        min_energy = np.log10(self.min_energy)
        max_energy = np.log10(self.max_energy)
        n_levels = (max_energy - min_energy) * 3 + 1
        levels = np.logspace(min_energy, max_energy, n_levels)
        x0 = self.xx[0]
        y0 = self.yy[0]
        for level in levels:
            a = np.interp(level, self.results[0], self.xx) - x0
            b = np.interp(level, self.results[1], self.yy) - y0
            el = Ellipse(xy=(x0, y0), width=a * 2, height=b * 2,
                         facecolor='none', edgecolor='red')
            ax = plt.gca()
            ax.add_artist(el)
        plt.axis('equal')
        plt.ylim(-self.yy[-1], self.yy[-1])
        plt.xlim(-self.xx[-1], self.xx[-1])


class DistancePairAreaEnergySensitivity(StationPairAreaEnergySensitivity):

    def __init__(self, distance, n):
        super(DistancePairAreaEnergySensitivity, self).__init__([102, 103])

        self.cluster = BaseCluster()
        if n == 8:
            self.cluster._add_station((distance / 2., 0, 0))
            self.cluster._add_station((-distance / 2., 0, 0))
        elif n == 4:
            detectors = [((-5, 0, 0), 'UD'), ((5, 0, 0), 'UD')]
            self.cluster._add_station((distance / 2., 0, 0), detectors=detectors)
            self.cluster._add_station((-distance / 2., 0, 0), detectors=detectors)

        # Throw showers along axis between stations and parallel at point
        # between the stations
        xc, yc, _ = self.cluster.calc_center_of_mass_coordinates()
        self.xx = np.arange(xc, self.max_radius + xc, self.step_size)
        self.yy = np.arange(yc, self.max_radius + yc, self.step_size)


def generate_regular_grid_positions(n, x0, y0=None, x1=None, y1=None):
    """ Generate positions on a regular grid bound by (x0, y0) and (x1, y1)

    :return: x, y

    """
    if y0 is None:
        y0 = x0

    if x1 is None and y1 is None:
        x1 = -x0
        y1 = -y0

    n_x = np.sqrt(n)
    n_y = n / n_x

    for x in np.linspace(x0, x1, n_x):
        for y in np.linspace(y0, y1, n_y):
            yield x, y


def generate_positions(self, n, max_r):
    """ Generate positions and an orientation uniformly on a circle

    :return: r, phi

    """
    for i in range(n):
        phi = np.random.uniform(-np.pi, np.pi)
        r = np.sqrt(np.random.uniform(0, max_r ** 2))
        yield r, phi


def get_pair_distance_energy_array(distances, energies, n=8):
    results = []
    for distance in pbar(distances):
        sens = DistancePairAreaEnergySensitivity(distance=distance, n=n)
        sens.main()
        areas = sens.get_area_energy(energies)
        results.append(areas)
    results = np.array(results)
    return results


def plot_results(distances, energies, results):
    plot = Plot('loglog')
    plot.histogram2d(np.log10(results[:-1, :-1] + 10), distances, energies,
                     bitmap=True)
    plot.set_ylabel('Shower energy')
    plot.set_xlabel('Distance between stations')
    plot.save_as_pdf('distance_energy_v_area')


if __name__ == "__main__":
    pair = [509, 505]
    sens = StationPairAreaEnergySensitivity(pair)
    sens.main()

    plt.figure()
    sens.show_restults()
    plt.show()
