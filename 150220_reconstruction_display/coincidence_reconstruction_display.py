import tables
from math import cos, sin
from numpy import nan_to_num, nanmin, isnan
from artist import Plot, MultiPlot

from sapphire.clusters import HiSPARCStations
from sapphire.analysis import coincidence_queries, event_utils


COIN_DATA = '/Users/arne/Datastore/esd_coincidences/coincidences_n7_120101_140801.h5'
OFFSETS =  {501: [-1.10338, 0.0000, 5.35711, 3.1686],
            502: [-8.11711, -8.5528, -8.72451, -9.3388],
            503: [-22.9796, -26.6098, -22.7522, -21.8723],
            504: [-15.4349, -15.2281, -15.1860, -16.5545],
            505: [-21.6035, -21.3060, -19.6826, -25.5366],
            506: [-20.2320, -15.8309, -14.1818, -14.1548],
            508: [-26.2402, -24.9859, -24.0131, -23.2882],
            509: [-24.8369, -23.0218, -20.6011, -24.3757]}
DETECTOR_IDS = [0, 1, 2, 3]


def display_coincidences(coincidence_events, reconstruction, c_id):
    cluster = HiSPARCStations(range(501, 511))

    ts0 = coincidence_events[0][1]['ext_timestamp']

    x = []
    y = []
    t = []
    p = []

    plot = Plot(width=r'.6\linewidth', height=r'.5\linewidth')

    for station_number, event in coincidence_events:
        if station_number == 507:
            continue
        station = cluster.get_station(station_number)
        sx, sy, _ = station.get_xyalpha_coordinates()
        for detector in station.detectors:
            dx, dy = detector.get_xy_coordinates()
            x.append(dx)
            y.append(dy)
        t.extend(event_utils.relative_detector_arrival_times(
                    event, ts0, DETECTOR_IDS, offsets=OFFSETS[station_number]))
        p.extend(event_utils.detector_densities(event, DETECTOR_IDS))

    mint = nanmin(t)

    xx = []
    yy = []
    tt = []
    pp = []

    for xv, yv, tv, pv in zip(x, y, t, p):
        if isnan(tv) or isnan(pv):
            plot.scatter([xv], [yv], mark='diamond')
        else:
            xx.append(xv)
            yy.append(yv)
            tt.append(tv - mint)
            pp.append(pv)

    plot.scatter_table(xx, yy, tt, pp)

    dx = cos(reconstruction['azimuth'])
    dy = sin(reconstruction['azimuth'])
    direction_length = reconstruction['zenith'] * 200
    core_x = reconstruction['x']
    core_y = reconstruction['y']

    plot.scatter([core_x], [core_y], mark='10-pointed star')
    plot.plot([core_x, core_x + direction_length * dx],
              [core_y, core_y + direction_length * dy], mark=None)

    plot.set_scalebar(location="lower left")
    plot.set_slimits(min=1, max=60)
    plot.set_colorbar('$\Delta$t [\si{n\second}]')
    plot.set_axis_equal()
    plot.set_xlimits(min=-250, max=350)
    plot.set_ylimits(min=-250, max=250)

    plot.set_xlabel('x [\si{\meter}]')
    plot.set_ylabel('y [\si{\meter}]')

    plot.save_as_pdf('event_display_%d' % c_id)


if __name__ == '__main__':
    with tables.open_file(COIN_DATA, 'r') as data:
        cq = coincidence_queries.CoincidenceQuery(data)
        for c_id in range(30):
            coincidence = cq.coincidences[c_id]
            coincidence_events = cq.events_from_stations([coincidence],
                                                         range(501, 511)).next()
            reconstruction = cq._get_reconstruction(coincidence)
            display_coincidences(coincidence_events, reconstruction, c_id)
