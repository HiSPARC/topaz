"""Determine accuracy of GPS positions

Compare multiple GPS self-surveys from stations.
- Get current location as initial reference
- Find previous locations close to it.
- Calculate center mass location of those positions.
- Get distance of each location to the center mass

Data contaminations:
- Short self-surveys. Partly mitigated by starting with the current location,
  which should be a 24h survey.
- Actually moved GPS antennae. Partly removed by requiring locations to be
  close to current
- Stations aving a different GPS location and then returning to a precious one
  by being manually entered, Source TSV already filtered equal positions if
  consecutive, by using 'set' on the distances spread out recurrances are
  also filtered.

"""
from numpy import arange, array, histogram, mean, percentile, sqrt

from artist import Plot

from sapphire import HiSPARCNetwork


def calculate_distances_to_cm(network):
    distr = []
    dist_hor = []
    dist_ver = []
    for station in network.stations:
        ref_x, ref_y, ref_z, _ = station.get_coordinates()
        x = array(station.x)
        y = array(station.y)
        z = array(station.z)
        distances = sqrt((x - ref_x) ** 2 + (y - ref_y) ** 2 + (z - ref_z) ** 2)
        close_by = distances < 15
        if len(close_by) > 3:
            # print station.number, len(close_by)
            filtered_x = x.compress(close_by)
            filtered_y = y.compress(close_by)
            filtered_z = z.compress(close_by)
            center_mass_x = mean(filtered_x)
            center_mass_y = mean(filtered_y)
            center_mass_z = mean(filtered_z)
            cm_distances = sqrt(
                (filtered_x - center_mass_x) ** 2
                + (filtered_y - center_mass_y) ** 2
                + (filtered_z - center_mass_z) ** 2
            )
            hor_distances = sqrt((filtered_x - center_mass_x) ** 2 + (filtered_y - center_mass_y) ** 2)
            ver_distances = sqrt((filtered_z - center_mass_z) ** 2)
            distr.extend(set(cm_distances.tolist()))
            dist_hor.extend(set(hor_distances.tolist()))
            dist_ver.extend(set(ver_distances.tolist()))
    return distr, dist_hor, dist_ver


def plot_distributions(distances, name=''):
    bins = arange(0, 10.001, 0.2)
    plot = Plot()
    plot.histogram(*histogram(distances, bins))
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=0, max=10)
    plot.set_ylabel('Counts')
    plot.set_xlabel(r'Distance to center mass location [\si{\meter}]')
    plot.set_label(r'67\%% within %.1fm' % percentile(distances, 67))
    plot.save_as_pdf('gps_distance_cm' + name)


def plot_distributions_all(distances, distances_hor, distances_ver):
    bins = arange(0, 10.001, 0.25)
    plot = Plot()
    # plot.histogram(*histogram(distances, bins))
    plot.histogram(*histogram(distances_hor, bins))
    plot.histogram(*histogram(distances_ver, bins - 0.02), linestyle='gray')
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=0, max=6)
    plot.set_ylabel('Counts')
    plot.set_xlabel(r'Distance to center mass location [\si{\meter}]')
    plot.save_as_pdf('gps_distance_cm_all')


if __name__ == "__main__":
    if "network" not in globals():
        network = HiSPARCNetwork()
    distr, dist_hor, dist_ver = calculate_distances_to_cm(network)
    plot_distributions(distr)
    plot_distributions(dist_hor, '_horizontal')
    plot_distributions(dist_ver, '_vertical')
    plot_distributions_all(distr, dist_hor, dist_ver)
