import warnings

import tables

from sapphire import HiSPARCStations, GroundParticlesSimulation


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cluster = HiSPARCStations([501, 502, 503, 504, 505, 506, 508, 509,
                                   510, 511])
    corsika_path = 'corsika.h5'

    with tables.open_file('result.h5', 'w') as result:
        sim = GroundParticlesSimulation(
            corsikafile_path=corsika_path, max_core_distance=1006.58,
            cluster=cluster, datafile=result, output_path='/', N=100000,
            seed=153957, progress=False)
        sim.run()
        sim.finish()
