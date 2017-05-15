import argparse

from itertools import cycle

from numpy import array
from smopy import Map

from artist import Plot

from sapphire import HiSPARCStations, Station


def get_detector_locations(station):
    """Detector LLA locations for the detectors of a single station"""
    latitudes = []
    longitudes = []

    cluster = HiSPARCStations([station], force_stale=True)

    station = cluster.get_station(station)
    for timestamp in station.detectors[0].timestamps:
        cluster.set_timestamp(timestamp)
        for detector in station.detectors:
            lat, lon, _ = detector.get_lla_coordinates()
            if abs(lat) <= 0.01 or abs(lon) <= 0.01:
                continue
            latitudes.append(lat)
            longitudes.append(lon)
    return latitudes, longitudes


def get_station_locations(station):
    """All GPS locations for a single station"""

    locations = Station(station, force_stale=True).gps_locations
    return locations['latitude'], locations['longitude']


def make_map(station=None, label='map', detectors=False):

    get_locations = (get_detector_locations if detectors
                     else get_station_locations)

    latitudes, longitudes = get_locations(station)

    bounds = (min(latitudes), min(longitudes),
              max(latitudes), max(longitudes))

    map = Map(bounds, margin=0, z=18)
    image = map.to_pil()

    map_w, map_h = image.size

    xmin, ymin = map.to_pixels(map.box[:2])
    xmax, ymax = map.to_pixels(map.box[2:])
    aspect = abs(xmax - xmin) / abs(ymax - ymin)

    width = 0.67
    height = width / aspect
    plot = Plot(width=r'%.2f\linewidth' % width,
                height=r'%.2f\linewidth' % height)

    plot.draw_image(image, 0, 0, map_w, map_h)
    plot.set_axis_equal()

    plot.set_xlimits(xmin, xmax)
    plot.set_ylimits(map_h - ymin, map_h - ymax)

    x, y = map.to_pixels(array(latitudes), array(longitudes))

    marks = cycle(['o'] * 4 + ['triangle'] * 4 + ['*'] * 4)
    colors = cycle(['black', 'red', 'green', 'blue'])
    if detectors:
        for xi, yi in zip(x, y):
            plot.scatter([xi], [map_h - yi],
                         markstyle="%s, thick" % colors.next(),
                         mark=marks.next())
    else:
        plot.scatter(x, map_h - y, markstyle="black!50!green")

    plot.set_xlabel('Longitude [$^\circ$]')
    plot.set_xticks([xmin, xmax])
    plot.set_xtick_labels(['%.4f' % x for x in (map.box[1], map.box[3])])

    plot.set_ylabel('Latitude [$^\circ$]')
    plot.set_yticks([map_h - ymin, map_h - ymax])
    plot.set_ytick_labels(['%.4f' % x for x in (map.box[0], map.box[2])])
#     plot.set_title(label)

    # save plot to file
    plot.save_as_pdf(label.replace(' ', '-'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int,
                        help=("Number of the country, cluster, subcluster, "
                              "or station (set to 0 when choosing network)"))
    parser.add_argument('--detectors', action='store_true',
                        help='Show each detector')
    args = parser.parse_args()

    label = 'station_%d' % args.number
    if args.detectors:
        label += '_detectors'

    label += '_4D'

    make_map(station=args.number, label=label, detectors=args.detectors)


if __name__ == '__main__':
    main()
