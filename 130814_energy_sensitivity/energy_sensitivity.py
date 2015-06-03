"""Energy sensitivity Science Park"""

from itertools import combinations
import pylab as plt
import numpy as np
import tables
import progressbar as pb

import sapphire.clusters
import sapphire.simulations
from sapphire.simulations.ldf import KascadeLdf


class EnergySensitivity(object):

    def __init__(self):
        # Detectors
        stations = [501, 502, 503, 504, 505, 506, 508, 509]
        self.cluster = sapphire.clusters.ScienceParkCluster(stations=stations)

        # Conditions
        # self.trig_threshold = 1.39  # density at one detector for 50% detection probability
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
        self.xx = np.linspace(-self.max_radius, self.max_radius, np.sqrt(self.grid_points))
        self.yy = np.linspace(-self.max_radius, self.max_radius, np.sqrt(self.grid_points))

    def main(self):

        progress = pb.ProgressBar(widgets=[pb.Percentage(), pb.Bar(), pb.ETA()])

        # Results
        self.results = [[self.find_min_energy(xc, yc) for xc in self.xx] for yc in progress(self.yy)]

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
            cluster_densities = self.calculate_densities_for_cluster(xc, yc, Ne)
            p_cluster = self.detection_probability_for_cluster(cluster_densities)
            if p_cluster == self.detection_probability:
                break
            elif p_cluster < self.detection_probability:
                lo = E
            else:
                hi = E
            E = 10 ** ((np.log10(lo) + np.log10(hi)) / 2.0)

        return E

    def detection_probability_for_cluster(self, cluster_densities):
        p_stations = [self.detection_probability_for_station(station_densities)
                      for station_densities in cluster_densities]
        p_combinations = list(combinations(p_stations, self.min_stations))
        p_station_combinations = [np.prod(p) for p in p_combinations]
        p_cluster = sum(p_station_combinations)

        return p_cluster

    def detection_probability_for_station(self, station_densities):
        p_detectors = [self.detection_probability_for_detector(density)
                       for density in station_densities]
        p_combinations = list(combinations(p_detectors, self.min_detectors))
        p_detector_combinations = [np.prod(p) for p in p_combinations]
        p_station = sum(p_detector_combinations)

        return p_station

    def detection_probability_for_detector(self, detector_density):
        p_detector = 1.0 - np.exp(- detector_density / 2.0)

        return p_detector

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
        density = self.ldf.get_ldf_value_for_size(r, Ne)

        return density

    def plot_scintillators_in_cluster(self):
        # Draw station locations on a map
        for station in self.cluster.stations:
            for detector in station.detectors:
                detector_x, detector_y = detector.get_xy_coordinates()
                plt.scatter(detector_x, detector_y, marker=',', c='m',
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
        # Draw Science Park Map on 1:1 scale (1 meter = 1 pixel)
        background = plt.imread("/Users/arne/Dropbox/hisparc/Code/topaz/"
                                "backgrounds/ScienceParkMap_1.092.png")
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
        # self.trig_threshold = 1.39  # density at one detector for 50% detection probability
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


# for every shower location around science park get distaces to stations,
# get detector densities from ldf
# check minimum energy to be detected..
# Plot over image of Science Park (easier to choose potential new locations)

# Simulation with Kascade LDF:
# file_path = paths('temp')
# data = tables.open_file(file_path, 'w')
# kascade_ldf = sapphire.simulations.KascadeLdfSimulation(cluster, data,
#        '/ldfsim/poisson_gauss_20', R=600, N=10000, use_poisson=True, gauss=.2, trig_threshold=.5)
# kascade_ldf.run(max_theta=pi / 3)
# data.close()

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
    sens = SingleFourEnergySensitivity()
#     sens.plot_scintillators_in_cluster()
#     sens.draw_background_map()
    sens.main()
    plt.show()
