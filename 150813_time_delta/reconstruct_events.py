from datetime import datetime

import tables
from numpy import genfromtxt, histogram, linspace, pi, where, degrees, invert

from artist import Plot

from sapphire import download_data, ReconstructESDEvents
from sapphire.transformations.clock import gps_to_datetime
from sapphire.utils import angle_between


def download_dataset():
    delta_data = genfromtxt('time_delta_fixed.tsv', delimiter='\t', dtype=None,
                      names=['ext_timestamp', 'time_delta'])
    start = gps_to_datetime(delta_data['ext_timestamp'][0] / int(1e9))
    end = gps_to_datetime(delta_data['ext_timestamp'][-1] / int(1e9))

    with tables.open_file('data.h5', 'w') as data:
        download_data(data, '/s501', 501, start, end)
        download_data(data, '/s501_original', 501, start, end)

    with tables.open_file('data.h5', 'a') as data:
        events = data.root.s501.events

        idx = delta_data['ext_timestamp'].tolist().index(events[-1]['ext_timestamp']) + 1
        time_delta = delta_data['time_delta'][:idx]
        t3 = data.root.s501.events.col('t3')[1:]
        t4 = data.root.s501.events.col('t4')[1:]
        events.modify_column(start=1, colname='t3', column=where(t3 >= 0, t3 + time_delta, t3))
        events.modify_column(start=1, colname='t4', column=where(t4 >= 0, t4 + time_delta, t4))
        events.flush()


def reconstruct_events():
    with tables.open_file('data.h5', 'a') as data:
        rec = ReconstructESDEvents(data, '/s501_original', 501, overwrite=True)
        rec.reconstruct_and_store()
        reco = ReconstructESDEvents(data, '/s501', 501, overwrite=True)
        reco.reconstruct_and_store()


def plot_reconstructions():
    with tables.open_file('data.h5', 'r') as data:
        rec = data.root.s501.reconstructions
        reco = data.root.s501_original.reconstructions

        # Compare azimuth distribution
        bins = linspace(-pi, pi, 20)  # Radians
        plot = Plot()
        plot.histogram(*histogram(rec.col('azimuth'), bins=bins))
        plot.histogram(*histogram(reco.col('azimuth'), bins=bins,
                       linestyle='red')
        plot.set_ylimits(min=0)
        plot.set_xlimits(-pi, pi)
        plot.set_ylabel('counts')
        plot.set_xlabel(r'Azimuth [\si{\radian}]')
        plot.save_as_pdf('azimuth')

        # Compare zenith distribution
        bins = linspace(0, pi / 2, 20)  # Radians
        plot = Plot()
        plot.histogram(*histogram(rec.col('zenith'), bins=bins))
        plot.histogram(*histogram(reco.col('zenith'), bins=bins),
                       linestyle='red')
        plot.set_ylimits(min=0)
        plot.set_xlimits(0, pi / 2)
        plot.set_ylabel('counts')
        plot.set_xlabel(r'Zenith [\si{\radian}]')
        plot.save_as_pdf('zenith')

        # Compare angles between old and new
        bins = linspace(0, 20, 20)  # Degrees
        plot = Plot()
        filter = (rec.col('zenith') > .5)
        d_angle = angle_between(rec.col('zenith'), rec.col('azimuth'),
                                reco.col('zenith'), reco.col('azimuth'))
        plot.histogram(*histogram(degrees(d_angle), bins=bins)))
        plot.histogram(*histogram(degrees(d_angle).compress(filter),
                       bins=bins), linestyle='red')
        plot.histogram(*histogram(degrees(d_angle).compress(invert(filter)),
                       bins=bins), linestyle='blue')
        plot.set_ylimits(min=0)
        plot.set_xlimits(0, 20)
        plot.set_ylabel('counts')
        plot.set_xlabel(r'Angle between [\si{\degree}]')
        plot.save_as_pdf('angle_between')


    def print_offsets()
        with tables.open_file('data.h5', 'r') as data:
            print data.root.s501.detector_offsets[:]
            print data.root.s501_original.detector_offsets[:]


if __name__ == "__main__":
    download_dataset()
    reconstruct_events()
    plot_reconstructions()
    print_offsets()
