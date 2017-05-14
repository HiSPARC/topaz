import glob
import os

from random import sample

import tables

from numpy import log10

OVERVIEW = '/data/hisparc/corsika/corsika_overview.h5'
DATADIR = '/data/hisparc/corsika/data'


def seeds_processed():
    """Get the seeds of simulations for which the h5 is already sorted"""

    files = glob.glob(os.path.join(DATADIR, '*_*/tmp_sorted_flag'))
    seeds = [os.path.basename(os.path.dirname(file)) for file in files]
    return set(seeds)


if __name__ == "__main__":
    available_seeds = seeds_processed()
    seeds = []
    with tables.open_file(OVERVIEW) as overview:
        sims = overview.get_node('/simulations')
        for e in set(log10(sims.col('energy'))):
            for z in set(sims.read_where('log10(energy) == e')['zenith']):
                selection = sims.read_where('(log10(energy) == e) & '
                                            '(zenith == z) & '
                                            '(particle_id == 14)')
                selected_seeds = ['%d_%d' % (row['seed1'], row['seed2'])
                                  for row in selection]
                possible_seeds = available_seeds.intersection(selected_seeds)
                if len(possible_seeds):
                    seeds.append(sample(possible_seeds, 1)[0])
                else:
                    print 'no suitable shower for E=%s, z=%.2f' % (e, z)

    with open('seed_list.txt', 'w') as seed_list:
        for seed in seeds:
            seed_list.write('%s\n' % seed)
