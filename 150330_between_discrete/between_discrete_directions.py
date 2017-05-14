import itertools

import numpy as np

from artist import Plot, PolarPlot

from sapphire.analysis.direction_reconstruction import DirectAlgorithmCartesian2D
from sapphire.clusters import SingleDiamondStation
from sapphire.utils import angle_between

TIME_RESOLUTION = 2.5  # nanoseconds
C = .3  # lightspeed m/ns
COLORS = ['black', 'red', 'green', 'blue']


def generate_discrete_times(station, detector_ids=[0, 2, 3]):
    """Generates possible arrival times for detectors

    The times are relative to the first detector, which is assumed to be
    at t = 0.

    """
    r = station_size(station, detector_ids)
    max_dt = ceil_in_base(r / C, TIME_RESOLUTION)
    times = np.arange(-max_dt, max_dt, TIME_RESOLUTION)
    time_combinations = itertools.product(times, repeat=len(detector_ids) - 1)
    return time_combinations


def station_size(station, detector_ids=[0, 2, 3]):
    """Get the largest distance between any two detectors in a station

    :param detectors: list of :class:`sapphire.clusters.Detector` objects

    """
    r = [station.calc_r_and_phi_for_detectors(d0, d1)[0]
         for d0, d1 in itertools.combinations(detector_ids, 2)]
    return max(r)


def ceil_in_base(value, base):
    return base * np.ceil(value / base)


def reconstruct_for_detectors(ids):
    times = generate_discrete_times(station, detector_ids=ids)
    detectors = [station.detectors[id].get_coordinates() for id in ids]
    x, y, z = zip(*detectors)

    angles = (dirrec.reconstruct_common((0,) + t, x, y, z) for t in times)
    angles = set([(round(t, 5), round(p, 5)) for t, p in angles
                  if not np.isnan(t) and not np.isnan(p)])
    return angles


def plot_discrete(angles):
    theta, phi = zip(*angles)
    graph = PolarPlot(use_radians=True)
    graph.scatter(phi, theta, markstyle='mark size=.5pt')

    graph.set_ylimits(0, np.pi / 2)
    graph.set_yticks([0, np.pi / 6, np.pi / 3, np.pi / 2])
    graph.set_ytick_labels([r'$0$', r'$\frac{1}{6}\pi$',
                            r'$\frac{2}{6}\pi$', r'$\frac{1}{2}\pi$', ])
    graph.set_ylabel('Zenith [rad]')
    graph.set_xlabel('Azimuth [rad]')
    graph.save_as_pdf('discrete_directions')


def angles_between_discrete(angles):
    theta, phi = zip(*angles)
    distances = angle_between(0., 0., np.array(theta), np.array(phi))
    counts, bins = np.histogram(distances, bins=np.linspace(0, np.pi, 721))
    plotd = Plot()
    plotd.histogram(counts, np.degrees(bins))
    # plotd.set_title('Distance between reconstructed angles for station and cluster')
    plotd.set_xlabel('Angle between reconstructions [\si{\degree}]')
    plotd.set_ylabel('Counts')
    plotd.set_xlimits(min=0, max=90)
    plotd.set_ylimits(min=0)
    plotd.save_as_pdf('angle_between_Zenith_discrete')

    plotd = Plot()
    distances = []
    for t, p in angles:
        distances.extend(angle_between(t, p, np.array(theta), np.array(phi)))
    counts, bins = np.histogram(distances, bins=np.linspace(0, np.pi, 361))
    plotd.histogram(counts, np.degrees(bins))
    # plotd.set_title('Distance between reconstructed angles for station and cluster')
    plotd.set_xlabel('Angle between reconstructions [\si{\degree}]')
    plotd.set_ylabel('Counts')
    plotd.set_xlimits(min=0, max=90)
    plotd.set_ylimits(min=0)
    plotd.save_as_pdf('angle_between_Zenith_discrete_all')


if __name__ == '__main__':

    dirrec = DirectAlgorithmCartesian2D()

    station = SingleDiamondStation().stations[0]

    angles = reconstruct_for_detectors([0, 1, 2])
    plot_discrete(angles)
    angles_between_discrete(angles)
