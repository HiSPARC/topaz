import os.path

import tables
from numpy import isnan

from sapphire import CoincidenceQuery


DATASTORE = "/Users/arne/Datastore/check_reconstructions"


def analyse_reconstructions(data):
    cq = CoincidenceQuery(data)
    total_count = cq.reconstructions.nrows
    succesful_direction = sum(~isnan(cq.reconstructions.col('zenith')))
    succesful_fraction = 100. * succesful_direction / total_count
    print '%.2f%% successful out of %d coincidences' % (succesful_fraction,
                                                      total_count)


if __name__ == '__main__':
    path = os.path.join(DATASTORE, 'dataset_sciencepark_n10_151101_160201.h5')
    with tables.open_file(path, 'r') as data:
        analyse_reconstructions(data)
