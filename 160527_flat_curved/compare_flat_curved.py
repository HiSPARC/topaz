""" Perform simulations on the Science Park stations

Uses stations 501 through 511 (except 507).

- Perform simulations using CORSIKA simulated showers.
- Reconstruct using the flat regression algorithm.
- Reconstruct using first flat, then core (center mass), then curved algorithm.
- Reconstruct using curved algorithm using the simulated core positions.
- Compare results

"""

from __future__ import division

import os

import numpy as np
import tables

from smopy import TILE_SIZE, Map, num2deg

from artist import MultiPlot, Plot

from sapphire import CoincidenceQuery, GroundParticlesSimulation, ReconstructESDCoincidences, ScienceParkCluster
from sapphire.analysis import event_utils
from sapphire.analysis.direction_reconstruction import (
    CurvedRegressionAlgorithm, DirectAlgorithmCartesian, RegressionAlgorithm)
from sapphire.simulations.showerfront import CorsikaStationFront
from sapphire.transformations import geographic
from sapphire.utils import angle_between, c, distance_between

RESULT_PATH_2D = '/Users/arne/Datastore/flat_curved/simulation_2D.h5'
RESULT_PATH_3D = '/Users/arne/Datastore/flat_curved/simulation_3D.h5'
RESULT_PATH = '/Users/arne/Datastore/flat_curved/simulation.h5'
# 0 zenith 772067892_538968191
CORSIKA_PATH_0 = '/Users/arne/Datastore/flat_curved/corsika.h5'
# 225 zenith 79960790_507733806
CORSIKA_PATH = '/Users/arne/Datastore/flat_curved/corsika225.h5'

DETECTOR_IDS = [0, 1, 2, 3]


def perform_simulations(data):
    cluster = ScienceParkCluster(force_stale=True)
    sim = GroundParticlesSimulation(CORSIKA_PATH, 100, cluster, data, '/', 900)
    sim.run()
    sim.finish()


def reconstruct_simulations(data):
    cluster = data.root.coincidences._v_attrs['cluster']
    offsets = {s.number: [d.offset + s.gps_offset for d in s.detectors]
               for s in cluster.stations}

    # Default reconstruction currently first direction then core
    frec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_flat', cluster=cluster)
#     frec.direction.curved = CurvedRegressionAlgorithm()
#     frec.direction.direct = DirectAlgorithmCartesian
#     frec.direction.fit = RegressionAlgorithm
    frec.prepare_output()
    frec.offsets = offsets
    frec.reconstruct_directions()
    frec.reconstruct_cores()
    frec.store_reconstructions()

    # Reconstruct direction, then core, then direction again
    crec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_curved', cluster=cluster)
#     crec.direction.curved = CurvedRegressionAlgorithm()
#     crec.direction.direct = DirectAlgorithmCartesian
#     crec.direction.fit = RegressionAlgorithm
    crec.prepare_output()
    crec.offsets = offsets
    crec.reconstruct_directions()
    crec.reconstruct_cores()
    crec.reconstruct_directions()
    crec.store_reconstructions()

    # Reconstruct directions using the input core
    xrec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_xy', cluster=cluster)
#     xrec.direction.curved = CurvedRegressionAlgorithm()
#     xrec.direction.direct = DirectAlgorithmCartesian
#     xrec.direction.fit = RegressionAlgorithm
    xrec.prepare_output()
    xrec.offsets = offsets
    xrec.core_x = xrec.cq.coincidences.col('x')
    xrec.core_y = xrec.cq.coincidences.col('y')
    xrec.reconstruct_directions()
    xrec.store_reconstructions()


def plot_results(data):
    rec_paths = ['recs_flat', 'recs_curved', 'recs_xy']
    linestyles = ['solid', 'dotted', 'dashed']
    plot = Plot()
    for i, rec_path in enumerate(rec_paths):
        recs = data.get_node('/coincidences/%s' % rec_path)
        angles = angle_between(recs.col('zenith'), recs.col('azimuth'),
                               recs.col('reference_zenith'), recs.col('reference_azimuth'))
        dangles = np.degrees(angles)
        counts, bins = np.histogram(dangles, bins=np.arange(0, 25, .5))
        plot.histogram(counts, bins + (i / 10.), linestyle=linestyles[i])
    plot.set_xlimits(0, 25)
    plot.set_ylimits(0)
    plot.set_xlabel(r'Angle between [\si{\degree}]')
    plot.save_as_pdf('angle_between')


def make_map(cluster):
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


def plot_map(data):
    cluster = data.root.coincidences._v_attrs['cluster']

    map = make_map(cluster)
    cq = CoincidenceQuery(data)
    cq.reconstructions = cq.data.get_node('/coincidences', 'recs_curved')
    cq.reconstructed = True

    for i, coincidence in enumerate(cq.coincidences.read_where('N > 6')):
        if i > 50:
            break
        coincidence_events = next(cq.all_events([coincidence]))
        reconstruction = cq._get_reconstruction(coincidence)
        display_coincidences(cluster, coincidence_events, coincidence,
                             reconstruction, map)


def display_coincidences(cluster, coincidence_events, coincidence,
                         reconstruction, map):
    offsets = {s.number: [d.offset + s.gps_offset for d in s.detectors]
               for s in cluster.stations}
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
            event, ts0, DETECTOR_IDS, offsets=offsets[station_number]))
        p.extend(event_utils.detector_densities(event, DETECTOR_IDS))

    image = map.to_pil()

    map_w, map_h = image.size
    aspect = float(map_w) / float(map_h)
    width = 0.67
    height = width / aspect
    plot = Plot(width=r'%.2f\linewidth' % width,
                height=r'%.2f\linewidth' % height)

    plot.draw_image(image, 0, 0, map_w, map_h)

    x, y = map.to_pixels(np.array(latitudes), np.array(longitudes))
    mint = np.nanmin(t)

    xx = []
    yy = []
    tt = []
    pp = []

    for xv, yv, tv, pv in zip(x, y, t, p):
        if np.isnan(tv) or np.isnan(pv):
            plot.scatter([xv], [map_h - yv], mark='diamond')
        else:
            xx.append(xv)
            yy.append(map_h - yv)
            tt.append(tv - mint)
            pp.append(pv)

    plot.scatter_table(xx, yy, tt, pp)

    transform = geographic.FromWGS84ToENUTransformation(cluster.lla)

    # Plot reconstructed core
    dx = np.cos(reconstruction['azimuth'])
    dy = np.sin(reconstruction['azimuth'])
    direction_length = reconstruction['zenith'] * 300
    core_x = reconstruction['x']
    core_y = reconstruction['y']

    core_lat, core_lon, _ = transform.enu_to_lla((core_x, core_y, 0))
    core_x, core_y = map.to_pixels(core_lat, core_lon)
    plot.scatter([core_x], [image.size[1] - core_y], mark='10-pointed star',
                 markstyle='red')
    plot.plot([core_x, core_x + direction_length * dx],
              [image.size[1] - core_y,
               image.size[1] - (core_y - direction_length * dy)], mark=None)

    # Plot simulated core
    dx = np.cos(reconstruction['reference_azimuth'])
    dy = np.sin(reconstruction['reference_azimuth'])
    direction_length = reconstruction['reference_zenith'] * 300
    core_x = reconstruction['reference_x']
    core_y = reconstruction['reference_y']

    core_lat, core_lon, _ = transform.enu_to_lla((core_x, core_y, 0))
    core_x, core_y = map.to_pixels(core_lat, core_lon)
    plot.scatter([core_x], [image.size[1] - core_y], mark='asterisk',
                 markstyle='orange')
    plot.plot([core_x, core_x + direction_length * dx],
              [image.size[1] - core_y,
               image.size[1] - (core_y - direction_length * dy)], mark=None)

    plot.set_scalebar(location="lower left")
    plot.set_slimits(min=1, max=30)
    plot.set_colorbar('$\Delta$t [\si{n\second}]')
    plot.set_axis_equal()
    plot.set_colormap('viridis')

    nw = num2deg(map.xmin, map.ymin, map.z)
    se = num2deg(map.xmin + map_w / TILE_SIZE,
                 map.ymin + map_h / TILE_SIZE,
                 map.z)

    x0, y0, _ = transform.lla_to_enu((nw[0], nw[1], 0))
    x1, y1, _ = transform.lla_to_enu((se[0], se[1], 0))

    plot.set_xlabel('x [\si{\meter}]')
    plot.set_xticks([0, map_w])
    plot.set_xtick_labels([int(x0), int(x1)])

    plot.set_ylabel('y [\si{\meter}]')
    plot.set_yticks([0, map_h])
    plot.set_ytick_labels([int(y1), int(y0)])

    plot.save_as_pdf('map/event_display_%d' % coincidence['id'])


def plot_distance_vs_delay(data):
    colors = {501: 'black',
              502: 'red!80!black',
              503: 'blue!80!black',
              504: 'green!80!black',
              505: 'orange!80!black',
              506: 'pink!80!black',
              508: 'blue!40!black',
              509: 'red!40!black',
              510: 'green!40!black',
              511: 'orange!40!black'}

    cq = CoincidenceQuery(data)
    cq.reconstructions = cq.data.get_node('/coincidences', 'recs_curved')
    cq.reconstructed = True

    cluster = data.root.coincidences._v_attrs['cluster']
    offsets = {s.number: [d.offset + s.gps_offset for d in s.detectors]
               for s in cluster.stations}

    front = CorsikaStationFront()
    front_r = np.arange(500)
    front_t = front.delay_at_r(front_r)

    for i, coincidence in enumerate(cq.coincidences.read_where('N > 6')):
        if i > 50:
            break
        coincidence_events = next(cq.all_events([coincidence]))
        reconstruction = cq._get_reconstruction(coincidence)

        core_x = coincidence['x']
        core_y = coincidence['y']

        plot = MultiPlot(2, 1)
        splot = plot.get_subplot_at(0, 0)
        rplot = plot.get_subplot_at(1, 0)

        splot.plot(front_r, front_t, mark=None)

        ref_extts = coincidence_events[0][1]['ext_timestamp']

        front_detect_r = []
        front_detect_t = []

        for station_number, event in coincidence_events:
            station = cluster.get_station(station_number)
            t = event_utils.relative_detector_arrival_times(event, ref_extts,
                                                            offsets=offsets[station_number], detector_ids=DETECTOR_IDS)
            core_distances = []
            for i, d in enumerate(station.detectors):
                x, y, z = d.get_coordinates()
                core_distances.append(distance_between(core_x, core_y, x, y))
                t += d.get_coordinates()[-1] / c
            splot.scatter(core_distances, t, mark='o', markstyle=colors[station_number])
            splot.scatter([np.mean(core_distances)], [np.nanmin(t)], mark='*', markstyle=colors[station_number])
            rplot.scatter([np.mean(core_distances)], [np.nanmin(t) - front.delay_at_r(np.mean(core_distances))],
                          mark='*', markstyle=colors[station_number])

        splot.set_ylabel('Relative arrival time [ns]')
        rplot.set_ylabel(r'Residuals')
        rplot.set_axis_options(r'height=0.25\textwidth')
        splot.set_ylimits(-10, 150)

        plot.set_xlimits_for_all(None, 0, 400)
        plot.set_xlabel('Distance from core [m]')
        plot.show_xticklabels(1, 0)
        plot.show_yticklabels_for_all()

        plot.save_as_pdf('front_shape/distance_v_time_%d_core' % coincidence['id'])


if __name__ == "__main__":
    if not os.path.exists(RESULT_PATH):
        with tables.open_file(RESULT_PATH, 'w') as data:
            perform_simulations(data)
    with tables.open_file(RESULT_PATH, 'a') as data:
        if ('/coincidences/recs_flat' not in data or
                '/coincidences/recs_curved' not in data or
                '/coincidences/recs_xy' not in data):
            reconstruct_simulations(data)
    with tables.open_file(RESULT_PATH, 'r') as data:
        plot_results(data)
        plot_distance_vs_delay(data)
        plot_map(data)
