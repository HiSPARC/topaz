from math import cos, sin

import tables

from numpy import append, arange, array, insert, isnan, nanmin
from smopy import TILE_SIZE, Map, num2deg

from artist import Plot

from sapphire import CoincidenceQuery, HiSPARCStations, Station
from sapphire.analysis import event_utils
from sapphire.transformations import geographic

COIN_DATA = '/Users/arne/Datastore/esd_coincidences/coincidences_n7_120101_140801.h5'
OFFSETS = {
    501: [-1.10338, 0.0000, 5.35711, 3.1686],
    502: [-8.11711, -8.5528, -8.72451, -9.3388],
    503: [-22.9796, -26.6098, -22.7522, -21.8723],
    504: [-15.4349, -15.2281, -15.1860, -16.5545],
    505: [-21.6035, -21.3060, -19.6826, -25.5366],
    506: [-20.2320, -15.8309, -14.1818, -14.1548],
    508: [-26.2402, -24.9859, -24.0131, -23.2882],
    509: [-24.8369, -23.0218, -20.6011, -24.3757],
}
DETECTOR_IDS = [0, 1, 2, 3]
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509]
CLUSTER = HiSPARCStations(STATIONS)
COLORS = ['black', 'red!80!black', 'green!80!black', 'blue!80!black']


def make_map(cluster=CLUSTER):
    latitudes = []
    longitudes = []

    for station in cluster.stations:
        for detector in station.detectors:
            latitude, longitude, _ = detector.get_lla_coordinates()
            latitudes.append(latitude)
            longitudes.append(longitude)
    map = Map((min(latitudes), min(longitudes), max(latitudes), max(longitudes)))
    return map


def display_coincidences(coincidence_events, reconstruction, c_id, map):

    cluster = CLUSTER

    ts0 = coincidence_events[0][1]['ext_timestamp']

    latitudes = []
    longitudes = []
    t = []
    p = []

    for station_number, event in coincidence_events:
        if station_number == 507:
            continue
        station = cluster.get_station(station_number)
        for detector in station.detectors:
            latitude, longitude, _ = detector.get_lla_coordinates()
            latitudes.append(latitude)
            longitudes.append(longitude)
        t.extend(event_utils.relative_detector_arrival_times(event, ts0, DETECTOR_IDS, offsets=OFFSETS[station_number]))
        p.extend(event_utils.detector_densities(event, DETECTOR_IDS))

    image = map.to_pil()

    aspect = float(image.size[0]) / float(image.size[1])
    height = 0.67 / aspect
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

    dx = cos(reconstruction['azimuth'])
    dy = sin(reconstruction['azimuth'])
    direction_length = reconstruction['zenith'] * 300
    core_x = reconstruction['x']
    core_y = reconstruction['y']

    transform = geographic.FromWGS84ToENUTransformation(cluster.lla)
    core_lat, core_lon, _ = transform.enu_to_lla((core_x, core_y, 0))
    core_x, core_y = map.to_pixels(core_lat, core_lon)

    plot.scatter([core_x], [image.size[1] - core_y], mark='10-pointed star')
    plot.plot(
        [core_x, core_x + direction_length * dx],
        [image.size[1] - core_y, image.size[1] - (core_y - direction_length * dy)],
        mark=None,
    )

    plot.set_scalebar(location="lower left")
    plot.set_slimits(min=1, max=60)
    plot.set_colorbar(r'$\Delta$t [\si{n\second}]')
    plot.set_axis_equal()

    nw = num2deg(map.xmin, map.ymin, map.z)
    se = num2deg(map.xmin + image.size[0] / TILE_SIZE, map.ymin + image.size[1] / TILE_SIZE, map.z)

    x0, y0, _ = transform.lla_to_enu((nw[0], nw[1], 0))
    x1, y1, _ = transform.lla_to_enu((se[0], se[1], 0))

    plot.set_xlabel(r'x [\si{\meter}]')
    plot.set_xticks([0, image.size[0]])
    plot.set_xtick_labels([int(x0), int(x1)])

    plot.set_ylabel(r'y [\si{\meter}]')
    plot.set_yticks([0, image.size[1]])
    plot.set_ytick_labels([int(y1), int(y0)])

    #     plot.set_xlimits(min=-250, max=350)
    #     plot.set_ylimits(min=-250, max=250)
    #     plot.set_xlabel('x [\si{\meter}]')
    #     plot.set_ylabel('y [\si{\meter}]')

    plot.save_as_pdf('coincidences/event_display_%d_%d' % (c_id, ts0))


def plot_traces(coincidence_events):
    plot = Plot()
    t0 = int(coincidence_events[0][1]['ext_timestamp'])
    tick_labels = []
    tick_positions = []

    for i, station_event in enumerate(coincidence_events):
        station_number, event = station_event
        station = Station(station_number)
        traces = station.event_trace(event['timestamp'], event['nanoseconds'])
        start_trace = (int(event['ext_timestamp']) - t0) - event['t_trigger']
        t = arange(start_trace, start_trace + (2.5 * len(traces[0])), 2.5)
        t = insert(t, 0, -20000)
        t = append(t, 20000)
        # trace = array(traces).sum(0)
        for j, trace in enumerate(traces):
            if max(trace) <= 10:
                trace = array(trace)
            else:
                trace = array(trace) / float(max(trace)) * 100
            trace = insert(trace, 0, 0)
            trace = append(trace, 0)
            plot.plot(t, trace + (100 * j) + (500 * i), mark=None, linestyle=COLORS[j])
        tick_labels.append(station_number)
        tick_positions.append(500 * i)

    plot.set_yticks(tick_positions)
    plot.set_ytick_labels(tick_labels)
    plot.set_xlimits(min=-250, max=1300)
    plot.set_xlabel(r't [\si{n\second}]')
    plot.set_ylabel('Signal strength')

    plot.save_as_pdf('traces_%d' % t0)


if __name__ == '__main__':
    map = make_map(CLUSTER)
    with tables.open_file(COIN_DATA, 'r') as data:
        cq = CoincidenceQuery(data)
        #         coincidences = cq.all(STATIONS)
        #         for coincidence in coincidences[10:100]:
        coincidence = cq.coincidences[1999]
        coincidence_events = next(cq.events_from_stations([coincidence], STATIONS))
        reconstruction = cq._get_reconstruction(coincidence)
        display_coincidences(coincidence_events, reconstruction, coincidence['id'], map)

        plot_traces(coincidence_events)
