""" Compare the speed of running simulations on various corsika h5 files.

Different levels of compression and with/without sorting.

RESULTS for shower 852288981_412468522

Sorted files:
Complevel: 0, size: 354 MB, time: 12 s
Complevel: 1, size: 354 MB, time: 12 s
Complevel: 5, size: 354 MB, time: 12 s
Complevel: 9, size: 292 MB, time: 14 s

Unsorted file:
Complevel: 0, size: 380 MB, time: 697 s

"""
from timeit import default_timer as timer

import tables

from sapphire import GroundParticlesSimulation, HiSPARCStations

COMP_RESULT_PATH = 'output_l%d.h5'
COMP_CORSIKA_DATA = 'corsika_l%d.h5'

RESULT_PATH = 'output_l%d.h5'
CORSIKA_DATA = 'corsika.h5'


def run_simulation():
    cluster = HiSPARCStations([501, 502, 503, 504, 505, 506, 508, 509])
    for complevel in [0, 1, 5, 9]:
        with tables.open_file(COMP_RESULT_PATH % complevel, 'w') as data:
            start = timer()
            sim = GroundParticlesSimulation(
                COMP_CORSIKA_DATA % complevel,
                max_core_distance=300,
                cluster=cluster,
                datafile=data,
                output_path='/',
                N=50,
                seed=42,
            )
            sim.run()
            end = timer()
            sim.finish()
            print(complevel, end - start)

    print('This is the slow one..')
    with tables.open_file(RESULT_PATH, 'w') as data:
        start = timer()
        sim = GroundParticlesSimulation(
            CORSIKA_DATA, max_core_distance=300, cluster=cluster, datafile=data, output_path='/', N=50, seed=42
        )
        sim.run()
        end = timer()
        sim.finish()
        print('orig', end - start)


if __name__ == "__main__":
    run_simulation()
