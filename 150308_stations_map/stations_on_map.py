from numpy import array

from artist import Plot
from sapphire.api import Network, Station

from smopy import Map, num2deg, TILE_SIZE


def show_map():
    latitudes = []
    longitudes = []

    for station_number in Network().station_numbers(country=0):
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

    graph = Plot()

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

    # save graph to file
    graph.save_as_pdf('map')


if __name__ == '__main__':
    show_map()
