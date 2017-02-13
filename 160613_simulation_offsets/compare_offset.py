""" Perform simulations on the Science Park stations

Uses stations 501 through 511 (except 507).

- Perform simulations using CORSIKA simulated shower.
- Reconstruct using no offsets.
- Reconstruct using simulated offsets (implemented in SAPPHiRE)
- Reconstruct using subset of stations, nice triangle
- Reconstruct using simulated offsets and altitude correction
- Compare results

"""

from __future__ import division
import os

import tables
from numpy import histogram, linspace, pi

from artist import Plot, PolarPlot

from sapphire import (ScienceParkCluster, GroundParticlesSimulation,
                      ReconstructESDCoincidences)
from sapphire.utils import c


RESULT_PATH = '/Users/arne/Datastore/simulation_offsets/simulation.h5'
CORSIKA_PATH = '/Users/arne/Datastore/CORSIKA/79960790_507733806/corsika.h5'

DETECTOR_IDS = [0, 1, 2, 3]


def perform_simulations(data):
    cluster = ScienceParkCluster(force_stale=True)
    sim = GroundParticlesSimulation(CORSIKA_PATH, 300, cluster, data, '/', N=900)
    sim.run()
    sim.finish()


def reconstruct_simulations(data):

    # Reconstruct with simulated offsets
    rec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                     overwrite=True, progress=True,
                                     destination='recs', force_stale=True)
    rec.reconstruct_and_store()

    # Reconstruct without any offset
    nrec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_no_offset', force_stale=True)
    nrec.prepare_output()
    nrec.reconstruct_directions()
    nrec.store_reconstructions()

    # Use subset of stations for reconstructions
    station_numbers = [501, 503, 506]

    # Reconstruct using simulated offsets
    srec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_sub_offset', force_stale=True)
    rec.reconstruct_and_store(station_numbers)

    # Reconstruct without any offset
    nrec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_sub_no_offset', force_stale=True)
    nrec.prepare_output()
    nrec.reconstruct_directions(station_numbers)
    nrec.store_reconstructions()

    # Reconstruct using simulated offsets, and add offset for altitude (this is wrong)
    arec = ReconstructESDCoincidences(data, coincidences_group='/coincidences',
                                      overwrite=True, progress=True,
                                      destination='recs_sub_offset_alt', force_stale=True)
    arec.prepare_output()
    arec.offsets = {station.number: [station.gps_offset + d.offset +
                                     d.get_coordinates()[2] / c
                                     for d in station.detectors]
                    for station in arec.cluster.stations}
    arec.reconstruct_directions(station_numbers)
    arec.store_reconstructions()


def plot_results(data):
    plot = PolarPlot(use_radians=True)
    for rec_group, linestyle in [('recs', ''), ('recs_no_offset', 'red')]:
        recs = data.get_node('/coincidences', rec_group)
        azimuth = recs.col('azimuth')
        plot_azimuths(plot, azimuth, linestyle)
    plot.save_as_pdf('azimuths_alt')

    # Using subset of stations
    plot = PolarPlot(use_radians=True)
    for rec_group, linestyle in [('recs_sub_offset', ''), ('recs_sub_no_offset', 'red'), ('recs_sub_offset_alt', 'green')]:
        recs = data.get_node('/coincidences', rec_group)
        azimuth = recs.col('azimuth')
        plot_azimuths(plot, azimuth, linestyle)
    plot.save_as_pdf('azimuths_alt')


def plot_azimuths(plot, azimuth, linestyle=''):
    n, bins = histogram(azimuth, bins=linspace(-pi, pi, 21))
    plot.histogram(n, bins, linestyle=linestyle)
    plot.set_title('Azimuth distribution')
    plot.set_ylimits(min=0)
    plot.set_xlabel('Azimuth [rad]')
    plot.set_ylabel('Counts')


if __name__ == "__main__":
    if not os.path.exists(RESULT_PATH):
        with tables.open_file(RESULT_PATH, 'w') as data:
            perform_simulations(data)
    with tables.open_file(RESULT_PATH, 'a') as data:
        reconstruct_simulations(data)
    with tables.open_file(RESULT_PATH, 'r') as data:
        plot_results(data)
