import argparse

from numpy import array

from artist import Plot
from sapphire.api import Network, Station

from smopy import Map, num2deg, TILE_SIZE


def make_map(country=None, cluster=None, subcluster=None, station=None,
             label='map'):
    latitudes = []
    longitudes = []

    if station is None:
        station_numbers = Network().station_numbers(country=country,
                                                    cluster=cluster,
                                                    subcluster=subcluster)
    else:
        station_numbers = [station]

    for station_number in station_numbers:
        try:
            location = Station(station_number).location()
        except:
            continue
        if location['latitude'] == 0 or location['longitude'] == 0:
            continue
        latitudes.append(location['latitude'])
        longitudes.append(location['longitude'])

    map = Map((min(latitudes), min(longitudes),
               max(latitudes), max(longitudes)))
    map.save_png('map-tiles-background.png')
    image = map.to_pil()
    x, y = map.to_pixels(array(latitudes), array(longitudes))

    aspect = float(image.size[0]) / float(image.size[1])
    height = .67 / aspect

    graph = Plot(height=r'%.2f\linewidth' % height)


    # graph histogram
    graph.draw_image(image, 0, 0, image.size[0], image.size[1])
    graph.scatter(x, image.size[1] - y)

    graph.set_axis_equal()

    nw = ['%.4f' % i for i in num2deg(map.xmin, map.ymin, map.z)]
    se = ['%.4f' % i for i in num2deg(map.xmin + image.size[0] / TILE_SIZE,
                                      map.ymin + image.size[1] / TILE_SIZE,
                                      map.z)]

    graph.set_xlabel('Longitude [$^\circ$]')
    graph.set_xticks([0, image.size[0]])
    graph.set_xtick_labels([nw[1], se[1]])

    graph.set_ylabel('Latitude [$^\circ$]')
    graph.set_yticks([0, image.size[1]])
    graph.set_ytick_labels([se[0], nw[0]])

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
    args = parser.parse_args()

    if args.network:
        label = 'Network'
        make_map(label=label)
    elif args.country:
        label = 'Country %d' % args.number
        make_map(country=args.number, label=label)
    elif args.cluster:
        label = 'Cluster %d' % args.number
        make_map(cluster=args.number, label=label)
    elif args.subcluster:
        label = 'Subcluster %d' % args.number
        make_map(subcluster=args.number, label=label)
    elif args.station:
        label = 'Station %d' % args.number
        make_map(station=args.number, label=label)


if __name__ == '__main__':
    main()
