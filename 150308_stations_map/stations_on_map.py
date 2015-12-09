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

def get_weather_locations():
    latitudes = []
    longitudes = []

    station_numbers = [s['number']
                       for s in Network().stations_with_weather()]

    for station_number in station_numbers:
        location = Station(station_number).location()
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
             label='map', detectors=False, weather=False, knmi=False):

    if detectors:
        latitudes, longitudes = get_detector_locations(country, cluster,
                                                       subcluster, station)
    else:
        latitudes, longitudes = get_station_locations(country, cluster,
                                                      subcluster, station)

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
    map.save_png('map-tiles-background.png')
    image = map.to_pil()

    map_w, map_h = image.size
    aspect = float(map_w) / float(map_h)

    width = 0.67
    height = width / aspect
    plot = Plot(width=r'%.2f\linewidth' % width,
                 height=r'%.2f\linewidth' % height)

    plot.draw_image(image, 0, 0, map_w, map_h)
    plot.set_axis_equal()

    xmin, ymin = map.to_pixels(map.box[:2])
    xmax, ymax = map.to_pixels(map.box[2:])
    plot.set_xlimits(xmin, xmax)
    plot.set_ylimits(map_h - ymin, map_h - ymax)

    x, y = map.to_pixels(array(latitudes), array(longitudes))
    plot.scatter(x, map_h - y, markstyle="black!50!green, thick")

    if weather:
        x, y = map.to_pixels(array(weather_latitudes), array(weather_longitudes))
        plot.scatter(x, map_h - y, markstyle="black!50!red, thick")
    if knmi:
        x, y = map.to_pixels(array(knmi_latitudes), array(knmi_longitudes))
        plot.scatter(x, map_h - y, markstyle="black!50!blue, thick")

    plot.set_xlabel('Longitude [$^\circ$]')
#     plot.set_xticks([0, map_w])
#     plot.set_xtick_labels([nw[1], se[1]])

    plot.set_ylabel('Latitude [$^\circ$]')
#     plot.set_yticks([0, map_h])
#     plot.set_ytick_labels([se[0], nw[0]])

#     plot.set_title(label)

    # save plot to file
    plot.save_as_pdf(label.replace(' ', '-'))


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
    parser.add_argument('--weather', action='store_true',
                        help='Show all HiSPARC weather stations')
    parser.add_argument('--knmi', action='store_true',
                        help='Show all KNMI weather stations')
    args = parser.parse_args()

    if args.network:
        label = 'network'
        make_map(label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.country:
        label = 'country_%d' % args.number
        make_map(country=args.number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.cluster:
        label = 'cluster_%d' % args.number
        make_map(cluster=args.number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.subcluster:
        label = 'subcluster_%d' % args.number
        make_map(subcluster=args.number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)
    elif args.station:
        label = 'station_%d' % args.number
        make_map(station=args.number, label=label, detectors=args.detectors, weather=args.weather, knmi=args.knmi)


if __name__ == '__main__':
    main()
