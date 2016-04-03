from artist import Plot

from sapphire import HiSPARCStations
from sapphire.transformations.clock import gps_to_datetime

COLORS = ['black', 'red', 'green', 'blue']


def plot_detectors(cluster):
    station = cluster.stations[0]
    detectors = station.detectors
    timestamps = set(station.timestamps).union(detectors[0].timestamps)

    plot = Plot()

    for timestamp in sorted(timestamps):
        cluster.set_timestamp(timestamp)
        for i in range(4):
            x, y = detectors[i].get_xy_coordinates()
            plot.scatter([x], [y], mark='*', markstyle=COLORS[i])
        x, y = station.get_xy_coordinates()
        plot.scatter([x], [y], markstyle='purple')
        # print timestamp, gps_to_datetime(timestamp), x, y

    plot.set_xlabel(r'Easting [\si{\meter}]')
    plot.set_ylabel(r'Northing [\si{\meter}]')
    plot.set_axis_equal()
    plot.save_as_pdf('locations_%d' % station.number)


if __name__ == "__main__":
    for sn in range(501, 512):
        # print sn
        cluster = HiSPARCStations([sn], force_stale=True)
        plot_detectors(cluster)
