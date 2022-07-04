import os.path

from datetime import datetime

import tables

from numpy import histogram, linspace, pi

from artist import PolarPlot

from sapphire import ReconstructESDCoincidences, ScienceParkCluster, download_coincidences
from sapphire.analysis.direction_reconstruction import CoincidenceDirectionReconstruction
from sapphire.utils import memoize

DATASTORE = "/Users/arne/Datastore/esd_coincidences"
PATH = os.path.join(DATASTORE, 'sciencepark_n3_160110_160201.h5')


class CoinDirRecDetOff(CoincidenceDirectionReconstruction):
    """Only correct detector offsets"""

    @memoize
    def determine_best_offsets(self, station_numbers, ts0, offsets):
        off = {sn: offsets[sn].detector_timing_offset(ts0) for sn in station_numbers}
        return off


class CoinDirRecDirRef(CoincidenceDirectionReconstruction):
    """Use direct reference station, no intermediate stations"""

    @memoize
    def determine_best_offsets(self, station_numbers, ts0, offsets):
        ref_sn = 501

        off = {
            sn: [o + offsets[sn].station_timing_offset(ref_sn, ts0)[0] for o in offsets[sn].detector_timing_offset(ts0)]
            for sn in station_numbers
        }
        return off


def download_sciencepark_dataset_n3():
    """Download a dataset for analysis

    To be used to check correctness of handling station timing offsets

    """
    stations = list(range(501, 512))
    start = datetime(2016, 1, 10)
    end = datetime(2016, 2, 1)
    with tables.open_file(PATH, 'w') as data:
        download_coincidences(data, stations=stations, start=start, end=end, n=3)


def reconstruct_coincidences():
    station_numbers = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]
    cluster = ScienceParkCluster(station_numbers, force_stale=True)

    with tables.open_file(PATH, 'a') as data:
        # Use default
        rec = ReconstructESDCoincidences(data, destination='recs', overwrite=True, force_stale=True)
        rec.reconstruct_and_store(station_numbers)

        # Use direct, not intermediate stations
        rec = ReconstructESDCoincidences(data, destination='recs_direct_offsets', overwrite=True, force_stale=True)
        rec.direction = CoinDirRecDirRef(frec.cluster)
        rec.reconstruct_and_store(station_numbers)

        # Only detector offsets
        rec = ReconstructESDCoincidences(data, destination='recs_detector_offsets', overwrite=True, force_stale=True)
        rec.direction = CoinDirRecDetOff(drec.cluster)
        rec.reconstruct_and_store(station_numbers)


def plot_results():
    with tables.open_file(PATH, 'r') as data:
        suffix = '_501_503_506_'
        for rec_group in ['recs', 'recs_direct_offsets', 'recs_detector_offsets']:
            recs = data.get_node('/coincidences', rec_group)
            # azimuth = recs.col('azimuth')
            azimuth = recs.read_where('s501 & s503 & s506')['azimuth']
            plot_azimuths(azimuth, name=rec_group + suffix)


def plot_azimuths(azimuth, name=''):

    plot = PolarPlot(use_radians=True)
    n, bins = histogram(azimuth, bins=linspace(-pi, pi, 21))
    plot.histogram(n, bins)
    plot.set_title('Azimuth distribution')
    plot.set_ylimits(min=0)
    plot.set_xlabel('Azimuth [rad]')
    plot.set_ylabel('Counts')
    plot.save_as_pdf('azimuths_%s' % name)


if __name__ == "__main__":
    if not os.path.exists(PATH):
        download_sciencepark_dataset_n3()
    reconstruct_coincidences()
    plot_results()
