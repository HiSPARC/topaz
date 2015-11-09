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
from itertools import combinations
import pylab as plt
import numpy as np
import tables
import progressbar as pb

from sapphire import ScienceParkCluster
from sapphire.simulations.ldf import KascadeLdf
from sapphire.utils import pbar


class EnergySensitivity(object):

    def __init__(self):
        # Detectors
        stations = [501, 502, 503, 504, 505, 506, 508, 509, 511]
        self.cluster = ScienceParkCluster(stations=stations)

        # Conditions
        self.detection_probability = 0.5
        self.min_detectors = 2
        self.min_stations = 3

        # Shower parameters
        self.ldf = KascadeLdf()
        self.grid_points = 250000
        self.max_radius = 1000
        self.min_energy = 1e13
        self.max_energy = 1e21
        self.start_energy = 1e17
        self.bisections = 8

        # Throw showers in a regular grid around first station
        self.xx = np.linspace(-self.max_radius, self.max_radius,
                              np.sqrt(self.grid_points))
        self.yy = np.linspace(-self.max_radius, self.max_radius,
                              np.sqrt(self.grid_points))

    def main(self):
        # Results
        self.results = [[self.find_min_energy(xc, yc) for xc in self.xx]
                        for yc in pbar(self.yy)]

        # Show results
        self.plot_scintillators_in_cluster()
        self.plot_energy_acceptance()
        self.draw_background_map()

    def find_min_energy(self, xc, yc):
        # Use bisection to get to the final energy quicker
        E = self.start_energy
        lo = self.min_energy
        hi = self.max_energy
        for _ in range(self.bisections):
            Ne = 10 ** (np.log10(E) - 15 + 4.8)
            station_densities = self.calculate_densities_for_cluster(xc, yc, Ne)
            p_cluster = self.detection_probability_for_cluster(station_densities)
            if p_cluster == self.detection_probability:
                break
            elif p_cluster < self.detection_probability:
                lo = E
            else:
                hi = E
            E = 10 ** ((np.log10(lo) + np.log10(hi)) / 2.0)

        return E

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
        n_stations = len(p_stations)
        p_cluster = 0
        for n in range(self.min_stations, n_stations + 1):
            for i in combinations(range(n_stations), n):
                p_combination = 1.
                for j in range(n_stations):
                    if j in i:
                        # Probability of trigger
                        p_combination *= p_stations[j]
                    else:
                        # Probability of no trigger
                        p_combination *= 1.0 - p_stations[j]
                p_cluster += p_combination

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
        if len(station_densities) < self.min_detectors:
            # To few detectors
            return 0

        p_detectors = [self.P0(density) for density in detector_densities]
        n_detectors = len(p_detectors)
        p_station = 0
        for n in range(self.min_detectors, n_detectors + 1):
            for i in combinations(range(n_detectors), n):
                p_combination = 1.
                for j in range(n_detectors):
                    if j in i:
                        # At least one particle
                        p_combination *= 1.0 - p_detectors[j]
                    else:
                        # No particles
                        p_combination *= p_detectors[j]
                p_station += p_combination

        return p_station

    def P(self, detector_density):
        """Chance of at least one particle in detector"""

        return 1.0 - P0(detector_density)

    def P0(self, detector_density):
        """Chance of detecting no particle in a detector"""

        return np.exp(-detector_density / 2.0)

    def calculate_densities_for_cluster(self, x, y, Ne):
        densities = [self.calculate_densities_for_station(station, x, y, Ne)
                     for station in self.cluster.stations]

        return densities

    def calculate_densities_for_station(self, station, x, y, Ne):
        densities = [self.calculate_densities_for_detector(detector, x, y, Ne)
                     for detector in station.detectors]

        return densities

    def calculate_densities_for_detector(self, detector, x, y, Ne):
        x0, y0 = detector.get_xy_coordinates()
        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        density = self.ldf.calculate_ldf_value(r, Ne)

        return density

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
        C = plt.contour(self.xx, self.yy, self.results,
                        np.logspace(13, 21, 25))
        plt.clabel(C, np.logspace(13, 21, 9), inline=1, fontsize=8, fmt='%.0e')

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


class SingleFourEnergySensitivity(EnergySensitivity):

    def __init__(self):
        super(SingleFourEnergySensitivity, self).__init__()

        # Detectors
        self.cluster = sapphire.clusters.SingleStation()

        # Conditions
        self.detection_probability = 0.5
        self.min_detectors = 2
        self.min_stations = 1


class SingleTwoEnergySensitivity(SingleFourEnergySensitivity):

    def __init__(self):
        super(SingleTwoEnergySensitivity, self).__init__()

        # Detectors
        self.cluster = sapphire.clusters.SingleTwoDetectorStation()


class SingleDiamondEnergySensitivity(SingleFourEnergySensitivity):

    def __init__(self):
        super(SingleDiamondEnergySensitivity, self).__init__()

        # Detectors
        self.cluster = sapphire.clusters.SingleDiamondStation()


def generate_regular_grid_positions(self, N, x0, y0=None, x1=None, y1=None):
    """ Generate positions on a regular grid bound by (x0, y0) and (x1, y1)

    :return: x, y

    """
    if y0 is None:
        y0 = x0

    if x1 is None and y1 is None:
        x1 = -x0
        y1 = -y0

    N_x = np.sqrt(N)
    N_y = N / N_x

    for x in np.linspace(x0, x1, N_x):
        for y in np.linspace(y0, y1, N_y):
            yield x, y


def generate_positions(self, N, max_r):
    """ Generate positions and an orientation uniformly on a circle

    :return: r, phi

    """
    for i in range(N):
        phi = np.random.uniform(-np.pi, np.pi)
        r = np.sqrt(np.random.uniform(0, max_r ** 2))
        yield r, phi


if __name__ == "__main__":
    plt.figure()
    sens = EnergySensitivity()
    sens.main()
    plt.show()
