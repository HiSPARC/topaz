"""Energy sensitivity Science Park"""

import pylab as plt
import numpy as np
import tables

import sapphire.clusters
import sapphire.simulations
from sapphire.simulations.ldf import KascadeLdf

from paths import paths

class EnergySensitivity(object):
    def main(self):

        # Detectors
        stations = [501, 502, 503, 504, 505, 506, 508, 509]
        self.cluster = sapphire.clusters.ScienceParkCluster(stations=stations)

        # Conditions
        self.trig_threshold = 1.39 # density at detector for 50% detection probability
        self.min_detectors = 2
        self.min_stations = 1

        # Shower parameters
        self.grid_points = 100000
        self.max_radius = 600
        self.min_energy = 1e13
        self.max_energy = 1e21
        self.bisections = 5

        # Results
        self.results = []

        # Throw showers in a regular grid around first station
        self.xx = np.linspace(-self.max_radius, self.max_radius, np.sqrt(self.grid_points))
        self.yy = np.linspace(-self.max_radius, self.max_radius, np.sqrt(self.grid_points))

        for yc in self.yy:
            result_row = []
            for xc in self.xx:
                # Slowly increase the energy, go to next when detected
                for E in np.logspace(np.log10(self.min_energy),
                                     np.log10(self.max_energy), 100):
                    Ne = 10 ** (np.log10(E) - 15 + 4.8)
                    self.ldf = KascadeLdf(Ne)
                    if self.check_stations_with_triggers(xc, yc):
                        result_row.append(E)
                        break
                    if E == self.max_energy:
                        result_row.append(E)
            self.results.append(result_row)

        self.plot_scintillators_in_cluster()
        self.plot_energy_acceptance()
        self.draw_background_map()

    def check_stations_with_triggers(self, x, y):
        n_triggered = 0

        for station in self.cluster.stations:
            densities = self.calculate_densities_for_station(station, x, y)
            if self.check_station_has_triggered(densities):
                n_triggered += 1

        if n_triggered >= self.min_stations:
            enough_stations = True
        else:
            enough_stations = False

        return enough_stations

    def check_station_has_triggered(self, densities):
        """Check if a given station would trigger for given shower"""
        num_detectors_over_threshold = sum([True for u in densities
                                            if u >= self.trig_threshold])
        if num_detectors_over_threshold >= self.min_detectors:
            has_triggered = True
        else:
            has_triggered = False

        return has_triggered

#     def calculate_minimum_density_for_station(self, x, y):
#         densities = self.calculate_densities_for_station(station, x, y)
#         return np.min(densities, axis=0)

    def calculate_densities_for_station(self, station, x, y):
        densities = []
        for detector in station.detectors:
            densities.append(self.calculate_densities_for_detector(detector, x, y))
        return np.array(densities)

    def calculate_densities_for_detector(self, detector, x, y):
        x0, y0 = detector.get_xy_coordinates()

        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)

        return self.ldf.calculate_ldf_value(r)


    def plot_scintillators_in_cluster(self):
        # Draw station locations on a map
        for station in self.cluster.stations:
            for detector in station.detectors:
                detector_x, detector_y = detector.get_xy_coordinates()
                plt.scatter(detector_x, detector_y, marker=',', c='m', edgecolor='none', s=6)
            station_x, station_y, station_a = station.get_xyalpha_coordinates()
            plt.scatter(station_x, station_y, marker=',', c='b', edgecolor='none', s=3)

    def plot_energy_acceptance(self):
        # Grid
        plt.contour(self.xx, self.yy, self.results, np.logspace(13, 21, 25))
        C = plt.contour(self.xx, self.yy, self.results, np.logspace(13, 21, 25))
        plt.clabel(C, np.logspace(13, 21, 9), inline=1, fontsize=10, fmt='%.0e')

    def draw_background_map(self):
        # Draw Science Park Map on 1:1 scale (1 meter = 1 pixel)
        background = plt.imread("/Users/arne/Dropbox/hisparc/Code/topaz/backgrounds/"
                                "ScienceParkMap_1.092.png")
        # determine pixel:meter ratio for different OSM zoom levels at Science Park..
        bg_scale = 1.092
        bg_width = background.shape[1] * bg_scale
        bg_height = background.shape[0] * bg_scale
        plt.imshow(background, aspect='equal', alpha=0.5,
                   extent=[-bg_width, bg_width, -bg_height, bg_height])


# for every shower location around science park get distaces to stations,
# get detector densities from ldf
# check minimum energy to be detected..
# Plot over image of Science Park (easier to choose potential new locations)

# Simulation with Kascade LDF:
# file_path = paths('temp')
# data = tables.openFile(file_path, 'w')
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


if __name__=="__main__":
    plt.figure()
    sens = EnergySensitivity()
    sens.main()
    plt.show()
