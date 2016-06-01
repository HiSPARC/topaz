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

    rec_d = cq.data.get_node('/coincidences', 'reconstructions_detectors')
    total_count_d = rec_d.nrows
    succesful_direction_d = sum(~isnan(rec_d.col('zenith')))
    succesful_fraction_d = 100. * succesful_direction_d / total_count_d
    print '%.2f%% successful out of %d coincidences' % (succesful_fraction_d,
                                                        total_count_d)


if __name__ == '__main__':
    path = os.path.join(DATASTORE, 'dataset_sciencepark_n10_151101_160201.h5')
    with tables.open_file(path, 'r') as data:
        analyse_reconstructions(data)
