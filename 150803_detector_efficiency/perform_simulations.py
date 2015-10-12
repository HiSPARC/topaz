from __future__ import division

import os

from numpy.random import choice

from sapphire import CorsikaQuery
from sapphire.qsub import check_queue, submit_job
from sapphire.utils import pbar

OVERVIEW = '/data/hisparc/corsika/corsika_overview.h5'

SCRIPT = """\
#!/usr/bin/env bash

python << END
from __future__ import division
from math import sqrt
import tables
from sapphire import clusters, GroundParticlesSimulation

# Make cluster with 3 stations all with 'center mass' at (0, 0, 0)
station_size = 10
a = station_size / 2
b = a * sqrt(3)
c = b / 3
cluster = clusters.BaseCluster()

# Star station
detectors = [((0, b - c, 0), 'UD'), ((0, 0, 0), 'UD'),
             ((-a, -c, 0), 'LR'), ((a, -c, 0), 'LR')]
cluster._add_station((0, 0, 0), 0, detectors)

# Diamond station
detectors = [((0, b, 0), 'UD'), ((0, -b, 0), 'UD'),
             ((-a, 0, 0), 'LR'), ((a, 0., 0), 'LR')]
cluster._add_station((0, 0, 0), 0, detectors)

# Two detector station
detectors = [((-a, 0, 0), 'UD'), ((a, 0, 0), 'UD')]
cluster._add_station((0, 0, 0), 0, detectors)

# Three detector station
detectors = [((0, b, 0), 'UD'), ((-1e10, -b, 0), 'UD'),
             ((-a, 0, 0), 'LR'), ((a, 0., 0), 'LR')]
cluster._add_station((0, 0, 0), 0, detectors)

result_path = '/data/hisparc/adelaat/efficiency/{seeds}.h5'
shower_path = '/data/hisparc/corsika/data/{seeds}/corsika.h5'

with tables.open_file(shower_path, 'r') as data:
    max_r = min(max(data.root.groundparticles.col('r')), 500)

with tables.open_file(result_path, 'w') as data:
    sim = GroundParticlesSimulation(shower_path, max_r, cluster, data, '/', 50000, progress=False)
    sim.run()
    sim.finish()
END
"""


# Different stations to test:
#  -> diamand (501)
#  -> ster (503)
#  -> two detector (102)
#  -> driehoek (3 detectoren)
#     Use diamond or star and move one of the detectors VERY far in x direction

# Number of simulations to choose per parameter set
N = 10


def perform_simulations():
    cq = CorsikaQuery(OVERVIEW)
    s = []
    for energy in pbar(cq.available_parameters('energy', particle='proton')):
        for zenith in cq.available_parameters('zenith', particle='proton', energy=energy):
            sims = cq.simulations(particle='proton', zenith=zenith, energy=energy, iterator=False)
            selected_seeds = cq.seeds(sims)
            n = min(len(selected_seeds), N)
            for seeds in choice(selected_seeds, n, replace=False):
                if seeds in s:
                    continue
                if not os.path.exists('/data/hisparc/corsika/data/{seeds}/corsika.h5'.format(seeds=seeds)):
                    continue
                s.append(seeds)
                if energy >= 16:
                    perform_job(seeds, 'long')
                else:
                    perform_job(seeds, 'generic')
    cq.finish()


def perform_job(seeds, queue):
    script = SCRIPT.format(seeds=seeds)
    submit_job(script, seeds, queue)


if __name__ == "__main__":
    perform_simulations()
