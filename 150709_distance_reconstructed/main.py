from math import cos, sin

import tables
from numpy import nanmin, isnan, array, arange, insert, append, sqrt
from artist import Plot

from sapphire import Station, HiSPARCStations, CoincidenceQuery
from sapphire.utils import distance_between
from sapphire.analysis import event_utils
from sapphire.transformations import geographic
from sapphire.analysis.event_utils import relative_detector_arrival_times

COIN_DATA = '/Users/arne/Datastore/esd_coincidences/coincidences_n7_120101_140801.h5'
DETECTOR_IDS = [0, 1, 2, 3]
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509]
CLUSTER = HiSPARCStations(STATIONS)
OFFSETS = {501: [-1.10338, 0.0000, 5.35711, 3.1686],
           502: [-8.11711, -8.5528, -8.72451, -9.3388],
           503: [-22.9796, -26.6098, -22.7522, -21.8723],
           504: [-15.4349, -15.2281, -15.1860, -16.5545],
           505: [-21.6035, -21.3060, -19.6826, -25.5366],
           506: [-20.2320, -15.8309, -14.1818, -14.1548],
           508: [-26.2402, -24.9859, -24.0131, -23.2882],
           509: [-24.8369, -23.0218, -20.6011, -24.3757]}
COLORS = {501: 'black',
          502: 'red!80!black',
          503: 'blue!80!black',
          504: 'green!80!black',
          505: 'orange!80!black',
          506: 'pink!80!black',
          508: 'blue!40!black',
          509: 'red!40!black'}


if __name__ == "__main__":
    with tables.open_file(COIN_DATA, 'r') as data:
        cq = CoincidenceQuery(data)
        coincidence = cq.coincidences[4323]
        coincidence_events = next(cq.events_from_stations([coincidence], STATIONS))
        reconstruction = cq._get_reconstruction(coincidence)
        core_x = reconstruction['x']
        core_y = reconstruction['y']

        plot = Plot()

        ref_extts = coincidence_events[0][1]['ext_timestamp']

        distances = arange(1, 370, 1)
        times = (2.43 * (1 + distances / 30.) ** 1.55) + 20
        plot.plot(distances, times, mark=None)

        for station_number, event in coincidence_events:
            station = CLUSTER.get_station(station_number)
            offsets = OFFSETS[station_number]
            t = relative_detector_arrival_times(event, ref_extts, offsets=offsets)
            core_distances = []
            for d in station.detectors:
                x, y = d.get_xy_coordinates()
                core_distances.append(distance_between(core_x, core_y, x, y))
            plot.scatter(core_distances, t, mark='*', markstyle=COLORS[station_number])
        plot.set_ylabel('Relative arrival time [ns]')
        plot.set_xlabel('Distance from core [m]')
        plot.save_as_pdf('relative_arrival_times')
