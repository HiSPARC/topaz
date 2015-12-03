import argparse

from numpy import array

from artist import Plot
from sapphire import Network, Station, HiSPARCStations

from smopy import Map, num2deg, TILE_SIZE


def get_detector_locations(country=None, cluster=None, subcluster=None,
                           station=None):
    latitudes = []
    longitudes = []

    if station is None:
        station_numbers = Network().station_numbers(country=country,
                                                    cluster=cluster,
                                                    subcluster=subcluster)
    else:
        station_numbers = [station]

    cluster = HiSPARCStations(station_numbers)

    for station_number in station_numbers:
        station = cluster.get_station(station_number)
        for detector in station.detectors:
            lat, lon, _ = detector.get_lla_coordinates()
            if abs(lat) <= 0.01 or abs(lon) <= 0.01:
                continue
            latitudes.append(lat)
            longitudes.append(lon)
    return latitudes, longitudes


def get_station_locations(country=None, cluster=None, subcluster=None,
                          station=None):
    latitudes = []
    longitudes = []

    if station is None:
        station_numbers = Network().station_numbers(country=country,
                                                    cluster=cluster,
                                                    subcluster=subcluster)
    else:
        station_numbers = [station]

    for station_number in station_numbers:
        location = Station(station_number).location()
        if location['latitude'] == 0 or location['longitude'] == 0:
            continue
        latitudes.append(location['latitude'])
        longitudes.append(location['longitude'])
    return latitudes, longitudes


def make_map(country=None, cluster=None, subcluster=None, station=None,
             label='map', detectors=False):

    if detectors:
        latitudes, longitudes = get_detector_locations(country, cluster,
                                                       subcluster, station)
    else:
        latitudes, longitudes = get_station_locations(country, cluster,
                                                      subcluster, station)

    map = Map((min(latitudes), min(longitudes),
               max(latitudes), max(longitudes)), margin=.1)
    map.save_png('map-tiles-background.png')
    image = map.to_pil()

    map_w, map_h = image.size
    aspect = float(map_w) / float(map_h)

    width = 0.67
    height = width / aspect
    graph = Plot(width=r'%.2f\linewidth' % width,
                 height=r'%.2f\linewidth' % height)

    graph.draw_image(image, 0, 0, map_w, map_h)
    graph.set_axis_equal()

    xmin, ymin = map.to_pixels(map.box[:2])
    xmax, ymax = map.to_pixels(map.box[2:])
    graph.set_xlimits(xmin, xmax)
    graph.set_ylimits(map_h - ymin, map_h - ymax)

    x, y = map.to_pixels(array(latitudes), array(longitudes))
    graph.scatter(x, map_h - y, markstyle="black!50!green, thick")

    graph.set_xlabel('Longitude [$^\circ$]')
#     graph.set_xticks([0, map_w])
#     graph.set_xtick_labels([nw[1], se[1]])

    graph.set_ylabel('Latitude [$^\circ$]')
#     graph.set_yticks([0, map_h])
#     graph.set_ytick_labels([se[0], nw[0]])

#     graph.set_title(label)

    # save graph to file
    graph.save_as_pdf(label.replace(' ', '-'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int,
        help="Number of the country, cluster, subcluster, or station")
    parser.add_argument('--network', action='store_true',
                        help='Map of the whole network')
    parser.add_argument('--country', action='store_true',
                        help='Number represents the country')
    parser.add_argument('--cluster', action='store_true',
                        help='Number represents the cluster')
    parser.add_argument('--subcluster', action='store_true',
                        help='Number represents the subcluster')
    parser.add_argument('--station', action='store_true',
                        help='Number represents the station')
    parser.add_argument('--detectors', action='store_true',
                        help='Show each detector')
    args = parser.parse_args()

    if args.detectors:
        detectors = True
    else:
        detectors = False

    if args.network:
        label = 'network'
        make_map(label=label, detectors=detectors)
    elif args.country:
        label = 'country %d' % args.number
        make_map(country=args.number, label=label, detectors=detectors)
    elif args.cluster:
        label = 'cluster %d' % args.number
        make_map(cluster=args.number, label=label, detectors=detectors)
    elif args.subcluster:
        label = 'subcluster %d' % args.number
        make_map(subcluster=args.number, label=label, detectors=detectors)
    elif args.station:
        label = 'station %d' % args.number
        make_map(station=args.number, label=label, detectors=detectors)


if __name__ == '__main__':
    main()
