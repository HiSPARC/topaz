import tables

from numpy import append, arange, array, insert, isnan, nanmin
from smopy import TILE_SIZE, Map, num2deg

from artist import Plot

from sapphire import CoincidenceQuery, HiSPARCStations, Station
from sapphire.analysis import event_utils
from sapphire.transformations import geographic

COIN_DATA = '/Users/arne/Datastore/esd_coincidences/sciencepark_n11_150701_151105.h5'
# OFFSETS =  {501: [-1.10338, 0.0000, 5.35711, 3.1686],
#             502: [-8.11711, -8.5528, -8.72451, -9.3388],
#             503: [-22.9796, -26.6098, -22.7522, -21.8723],
#             504: [-15.4349, -15.2281, -15.1860, -16.5545],
#             505: [-21.6035, -21.3060, -19.6826, -25.5366],
#             506: [-20.2320, -15.8309, -14.1818, -14.1548],
#             508: [-26.2402, -24.9859, -24.0131, -23.2882],
#             509: [-24.8369, -23.0218, -20.6011, -24.3757]}
DETECTOR_IDS = [0, 1, 2, 3]
STATIONS = list(range(501, 512))
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
    map = Map((min(latitudes), min(longitudes),
               max(latitudes), max(longitudes)))
    return map


def display_coincidences(coincidence_events, c_id, map):

    cluster = CLUSTER

    ts0 = coincidence_events[0][1]['ext_timestamp']

    latitudes = []
    longitudes = []
    t = []
    p = []

    for station_number, event in coincidence_events:
        station = cluster.get_station(station_number)
        for detector in station.detectors:
            latitude, longitude, _ = detector.get_lla_coordinates()
            latitudes.append(latitude)
            longitudes.append(longitude)
        t.extend(event_utils.relative_detector_arrival_times(
            event, ts0, DETECTOR_IDS))
        p.extend(event_utils.detector_densities(event, DETECTOR_IDS))

    image = map.to_pil()

    map_w, map_h = image.size
    aspect = float(map_w) / float(map_h)
    width = 0.67
    height = width / aspect
    plot = Plot(width=r'%.2f\linewidth' % width,
                height=r'%.2f\linewidth' % height)

    plot.draw_image(image, 0, 0, map_w, map_h)

    x, y = map.to_pixels(array(latitudes), array(longitudes))
    mint = nanmin(t)

    xx = []
    yy = []
    tt = []
    pp = []

    for xv, yv, tv, pv in zip(x, y, t, p):
        if isnan(tv) or isnan(pv):
            plot.scatter([xv], [map_h - yv], mark='diamond')
        else:
            xx.append(xv)
            yy.append(map_h - yv)
            tt.append(tv - mint)
            pp.append(pv)

    plot.scatter_table(xx, yy, tt, pp)

    transform = geographic.FromWGS84ToENUTransformation(cluster.lla)

    plot.set_scalebar(location="lower left")
    plot.set_slimits(min=1, max=60)
    plot.set_colorbar(r'$\Delta$t [\si{n\second}]')
    plot.set_axis_equal()

    nw = num2deg(map.xmin, map.ymin, map.z)
    se = num2deg(map.xmin + map_w / TILE_SIZE,
                 map.ymin + map_h / TILE_SIZE,
                 map.z)

    x0, y0, _ = transform.lla_to_enu((nw[0], nw[1], 0))
    x1, y1, _ = transform.lla_to_enu((se[0], se[1], 0))

    plot.set_xlabel(r'x [\si{\meter}]')
    plot.set_xticks([0, map_w])
    plot.set_xtick_labels([int(x0), int(x1)])

    plot.set_ylabel(r'y [\si{\meter}]')
    plot.set_yticks([0, map_h])
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
            plot.plot(t, trace + (100 * j) + (500 * i), mark=None,
                      linestyle=COLORS[j])
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
        for coincidence in cq.coincidences:
            coincidence_events = next(cq.events_from_stations([coincidence], STATIONS))
            display_coincidences(coincidence_events, coincidence['id'], map)
