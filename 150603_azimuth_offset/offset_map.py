import time

from numpy import array, isnan, nanmin
from smopy import TILE_SIZE, Map, num2deg

from artist import Plot

from sapphire import HiSPARCStations, Station
from sapphire.transformations import geographic

STATIONS = [501, 502, 503, 504, 505, 506, 508, 509]
CLUSTER = HiSPARCStations(STATIONS)


def make_map(cluster=CLUSTER):
    latitudes = []
    longitudes = []

    for station in cluster.stations:
        for detector in station.detectors:
            latitude, longitude, _ = detector.get_lla_coordinates()
            latitudes.append(latitude)
            longitudes.append(longitude)
    map = Map((min(latitudes), min(longitudes),
               max(latitudes), max(longitudes)))
    return map


def display_offsets(map):

    cluster = CLUSTER

    latitudes = []
    longitudes = []
    t = []

    for station in cluster.stations:
        for detector in station.detectors:
            latitude, longitude, _ = detector.get_lla_coordinates()
            latitudes.append(latitude)
            longitudes.append(longitude)
        number = station.number
        offsets = Station(number).detector_timing_offset(int(time.time()))
        t.extend(offsets)
    p = [2] * len(t)

    image = map.to_pil()

    aspect = float(image.size[0]) / float(image.size[1])
    height = .67 / aspect
    plot = Plot(height=r'%.2f\linewidth' % height)

    plot.draw_image(image, 0, 0, image.size[0], image.size[1])

    x, y = map.to_pixels(array(latitudes), array(longitudes))
    mint = nanmin(t)

    xx = []
    yy = []
    tt = []
    pp = []

    for xv, yv, tv, pv in zip(x, y, t, p):
        if isnan(tv) or isnan(pv):
            plot.scatter([xv], [image.size[1] - yv], mark='diamond')
        else:
            xx.append(xv)
            yy.append(image.size[1] - yv)
            tt.append(tv - mint)
            pp.append(pv)

    plot.scatter_table(xx, yy, tt, pp)
    plot.set_colorbar(r'$\Delta$t [\si{n\second}]')
    plot.set_axis_equal()

    nw = num2deg(map.xmin, map.ymin, map.z)
    se = num2deg(map.xmin + image.size[0] / TILE_SIZE,
                 map.ymin + image.size[1] / TILE_SIZE,
                 map.z)

    transform = geographic.FromWGS84ToENUTransformation(cluster.lla)
    x0, y0, _ = transform.lla_to_enu((nw[0], nw[1], 0))
    x1, y1, _ = transform.lla_to_enu((se[0], se[1], 0))

    plot.set_xlabel(r'x [\si{\meter}]')
    plot.set_xticks([0, image.size[0]])
    plot.set_xtick_labels([int(x0), int(x1)])

    plot.set_ylabel(r'y [\si{\meter}]')
    plot.set_yticks([0, image.size[1]])
    plot.set_ytick_labels([int(y1), int(y0)])

    plot.save_as_pdf('offset_display')


if __name__ == '__main__':
    map = make_map(CLUSTER)
    display_offsets(map)
