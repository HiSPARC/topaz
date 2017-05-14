""" Create a map of HiSPARC stations

Use arguments to choose what to show. Either ther entire network or a specific
subset. To choose a subset provide arguments to select a specific country,
cluster, subcluster, stations, or a specific station. Additional options are
available to also show HiSPARC and KNMI weather stations.

Examples::

    ./stations_on_map --network 0
    ./stations_on_map --weather --knmi --network 0
    ./stations_on_map --country 20000
    ./stations_on_map --cluster 1000
    ./stations_on_map --subcluster 500
    ./stations_on_map --detectors --stations 102,104,105
    ./stations_on_map --detectors --station 501

"""
import argparse

from ast import literal_eval

from numpy import array
from smopy import Map

from artist import Plot

from sapphire import HiSPARCStations, Network, Station

NETWORK = Network(force_stale=True)


def get_detector_locations(country=None, cluster=None, subcluster=None,
                           station=None, stations=None):
    latitudes = []
    longitudes = []

    if station is not None:
        station_numbers = [station]
    elif stations is not None:
        station_numbers = stations
    else:
        station_numbers = NETWORK.station_numbers(country=country,
                                                  cluster=cluster,
                                                  subcluster=subcluster)

    cluster = HiSPARCStations(station_numbers, force_stale=True)

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
                          station=None, stations=None):
    latitudes = []
    longitudes = []

    if station is not None:
        station_numbers = [station]
    elif stations is not None:
        station_numbers = stations
    else:
        station_numbers = NETWORK.station_numbers(country=country,
                                                  cluster=cluster,
                                                  subcluster=subcluster)

    for station_number in station_numbers:
        location = Station(station_number, force_stale=True).gps_location()
        if location['latitude'] == 0 or location['longitude'] == 0:
            continue
        latitudes.append(location['latitude'])
        longitudes.append(location['longitude'])

    return latitudes, longitudes


def get_weather_locations():
    latitudes = []
    longitudes = []

    station_numbers = [s['number']
                       for s in NETWORK.stations_with_weather()]

    for station_number in station_numbers:
        location = Station(station_number, force_stale=True).gps_location()
        latitudes.append(location['latitude'])
        longitudes.append(location['longitude'])

    return latitudes, longitudes


def get_knmi_locations():
    latitudes = [52.165, 52.463, 52.924, 52.301, 53.255, 52.644, 53.393,
                 52.506, 52.101, 52.130, 52.896, 52.458, 53.225, 52.703,
                 52.061, 53.409, 52.437, 52.750, 53.125, 52.073, 53.196,
                 52.273, 51.442, 51.226, 51.527, 51.993, 51.448, 51.955,
                 51.972, 51.568, 51.858, 51.446, 51.657, 51.197, 50.910,
                 51.498]
    longitudes = [4.419, 4.575, 4.785, 4.774, 4.942, 4.979, 5.346, 4.603,
                  5.177, 5.274, 5.384, 5.526, 5.755, 5.889, 5.888, 6.196,
                  6.263, 6.575, 6.586, 6.650, 7.150, 6.897, 3.596, 3.862,
                  3.884, 4.124, 4.349, 4.444, 4.927, 4.933, 5.145, 5.414,
                  5.706, 5.764, 5.768, 6.196]
    return latitudes, longitudes


def make_map(country=None, cluster=None, subcluster=None, station=None,
             stations=None, label='map', detectors=False, weather=False,
             knmi=False):

    get_locations = (get_detector_locations if detectors
                     else get_station_locations)

    if (country is None and cluster is None and subcluster is None and
            station is None and stations is None):
        latitudes, longitudes = ([], [])
    else:
        latitudes, longitudes = get_locations(country, cluster,
                                              subcluster, station, stations)

    if weather:
        weather_latitudes, weather_longitudes = get_weather_locations()
    else:
        weather_latitudes, weather_longitudes = ([], [])

    if knmi:
        knmi_latitudes, knmi_longitudes = get_knmi_locations()
    else:
        knmi_latitudes, knmi_longitudes = ([], [])

    bounds = (min(latitudes + weather_latitudes + knmi_latitudes),
              min(longitudes + weather_longitudes + knmi_longitudes),
              max(latitudes + weather_latitudes + knmi_latitudes),
              max(longitudes + weather_longitudes + knmi_longitudes))

    map = Map(bounds, margin=.1)
#     map.save_png('map-tiles-background.png')
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

    if knmi:
        x, y = map.to_pixels(array(knmi_latitudes), array(knmi_longitudes))
        plot.scatter(x, map_h - y, mark='square',
                     markstyle="mark size=0.5pt, black!50!blue, thick, opacity=0.6")

    x, y = map.to_pixels(array(latitudes), array(longitudes))
    if detectors:
        mark_size = 1.5
    else:
        mark_size = 3
    plot.scatter(x, map_h - y, markstyle="mark size=%fpt, black!50!green, "
                                         "thick, opacity=0.9" % mark_size)

    if weather:
        x, y = map.to_pixels(array(weather_latitudes), array(weather_longitudes))
        plot.scatter(x, map_h - y, markstyle="mark size=1.5pt, black!30!red, thick, opacity=0.9")

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
    parser.add_argument('number', type=str,
                        help=("Number of the country, cluster, subcluster, "
                              "or station (set to 0 when choosing network)"))
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
    parser.add_argument('--stations', action='store_true',
                        help='Number represents the station')
    parser.add_argument('--detectors', action='store_true',
                        help='Show each detector')
    parser.add_argument('--weather', action='store_true',
                        help='Show all HiSPARC weather stations')
    parser.add_argument('--knmi', action='store_true',
                        help='Show all KNMI weather stations')
    args = parser.parse_args()

    label = ''

    if args.detectors:
        label += '_detectors'
    if args.weather:
        label += '_weather'
    if args.knmi:
        label += '_knmi'

    number = literal_eval(args.number)

    if args.network:
        label = 'network' + label
        make_map(label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.country:
        label = 'country_%d' % number + label
        make_map(country=number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.cluster:
        label = 'cluster_%d' % number + label
        make_map(cluster=number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.subcluster:
        label = 'subcluster_%d' % number + label
        make_map(subcluster=number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.station:
        label = 'station_%d' % number + label
        make_map(station=number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.stations:
        label = 'stations_%s' % '_'.join(str(n) for n in number) + label
        make_map(stations=number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    else:
        label = 'map' + label
        make_map(station=None, label=label, weather=args.weather, knmi=args.knmi)


if __name__ == '__main__':
    main()
