import os

import tables

from sapphire.simulations.showerfront import (
    FlatFrontSimulation, FlatFrontSimulationWithoutErrors,
    FlatFrontSimulation2D, FlatFrontSimulation2DWithoutErrors,
    ConeFrontSimulation)
from sapphire.clusters import BaseCluster, ScienceParkCluster, HiSPARCStations

from artist import Plot


PATH = '/Users/arne/Datastore/expected_dt/test_station_dt_spa.h5'


def lengthy_cluster():
    cluster = BaseCluster()
    detectors = [((0, -5, 0), 'UD'), ((0, 5, 0), 'UD')]
    for r in range(0, 1000, 100):
        cluster._add_station((r, 0, 0), 0, detectors)

    return cluster


def simulate_shower_front():
#     cluster = lengthy_cluster()
#     cluster = HiSPARCStations([504, 505])
    cluster = ScienceParkCluster()
    with tables.open_file(PATH, 'w') as data:
        sim = FlatFrontSimulation(cluster, data, '/flat', int(3e5))
        sim.run()
        sim = ConeFrontSimulation(700, cluster, data, '/cone', int(3e5))
        sim.run()


if __name__ == "__main__":
    if not os.path.exists(PATH):
        simulate_shower_front()
    else:
        print "Data file already exists, doing nothing."
