import os.path

import tables

from sapphire import ReconstructESDCoincidences
from sapphire.analysis.direction_reconstruction import (
    CoincidenceDirectionReconstructionDetectors)

DATASTORE = "/Users/arne/Datastore/check_reconstructions"


def reconstruct_data(data):
    rec = ReconstructESDCoincidences(data, overwrite=True)
    rec.reconstruct_and_store()


def reconstruct_data_using_detectors(data):
    rec_d = ReconstructESDCoincidences(data, overwrite=True,
                                       destination='reconstructions_detectors')
    rec_d.direction = CoincidenceDirectionReconstructionDetectors(rec_d.cluster)
    rec_d.reconstruct_and_store()


if __name__ == '__main__':
    path = os.path.join(DATASTORE, 'dataset_sciencepark_n10_151101_160201.h5')
    with tables.open_file(path, 'a') as data:
        reconstruct_data(data)
        reconstruct_data_using_detectors(data)
