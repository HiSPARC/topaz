import os.path

from datetime import datetime

import tables

from numpy import cos, histogram, linspace, mean, pi, radians, sqrt
from numpy.random import normal

from artist import Plot

from sapphire import ReconstructESDEvents, download_data
from sapphire.utils import norm_angle

DATASTORE = "/Users/arne/Datastore/zenith_integrals"
STATION_PATH = os.path.join(DATASTORE, 'dataset_spa_160101_160110.h5')
STATIONS = [501, 502, 503, 504, 505, 510, 511]
START = datetime(2016, 1, 1)
END = datetime(2016, 1, 5)


def download_dataset():
    with tables.open_file(STATION_PATH, 'w') as data:
        for station_number in STATIONS:
            download_data(
                data, '/s%d' % station_number, station_number, start=START, end=END, type='events', progress=True
            )


def reconstruct_data():
    for station_number in STATIONS:
        with tables.open_file(STATION_PATH, 'a') as data:
            rec = ReconstructESDEvents(data, '/s%d' % station_number, station_number, overwrite=True)
            rec.reconstruct_and_store()


def plot_pulseintegrals():

    station_number = 501
    in_bins = linspace(1, 15000, 200)
    ph_bins = linspace(10, 1500, 200)
    az_bins = linspace(-pi, pi, 40)
    ze_bins = linspace(0, pi / 2.0, 50)
    min_n = 1.5
    max_zenith = radians(45)

    with tables.open_file(STATION_PATH, 'r') as data:
        sn = data.get_node('/s%d' % station_number)
        n_filter = set(sn.events.get_where_list('(n1 >= min_n) & (n2 >= min_n) & (n4 >= min_n)'))
        z_filter = set(sn.reconstructions.get_where_list('(zenith < max_zenith) & d1 & d2 & d4'))
        filter = list(n_filter & z_filter)
        integrals = sn.events.col('integrals')[filter]
        pulseheights = sn.events.col('pulseheights')[filter]
        azimuths = sn.reconstructions.col('azimuth')[filter]
        zeniths = sn.reconstructions.col('zenith')[filter]

    plot = Plot()
    counts, az_bins = histogram(azimuths, bins=az_bins)
    plot.histogram(counts, az_bins)

    # Smoothed version of azimuth histogram to counter discreteness at low zenith.
    smoothing = normal(scale=radians(8), size=len(azimuths))
    counts, az_bins = histogram(norm_angle(azimuths + smoothing), bins=az_bins)
    plot.histogram(counts, az_bins, linestyle='gray')

    plot.draw_horizontal_line(mean(counts), linestyle='red')
    plot.draw_horizontal_line(mean(counts) + sqrt(mean(counts)), linestyle='dashed, red')
    plot.draw_horizontal_line(mean(counts) - sqrt(mean(counts)), linestyle='dashed, red')
    plot.set_ylimits(min=0)
    plot.set_xlimits(-pi, pi)
    plot.save_as_pdf('azimuth')

    plot = Plot()
    counts, ze_bins = histogram(zeniths, bins=ze_bins)
    plot.histogram(counts, ze_bins)
    plot.set_ylimits(min=0)
    plot.set_xlimits(0, pi / 2)
    plot.save_as_pdf('zeniths')

    for i in range(4):
        plot = Plot('semilogy')
        counts, in_bins = histogram(integrals[:, i], bins=in_bins)
        plot.histogram(counts, in_bins)
        counts, in_bins = histogram(integrals[:, i] * cos(zeniths), bins=in_bins)
        plot.histogram(counts, in_bins, linestyle='red')
        plot.set_ylimits(min=1)
        plot.save_as_pdf('integrals_%d' % i)

        plot = Plot('semilogy')
        counts, ph_bins = histogram(pulseheights[:, i], bins=ph_bins)
        plot.histogram(counts, ph_bins)
        counts, ph_bins = histogram(pulseheights[:, i] * cos(zeniths), bins=ph_bins)
        plot.histogram(counts, ph_bins, linestyle='red')
        plot.set_ylimits(min=1)
        plot.save_as_pdf('pulseheights_%d' % i)


if __name__ == "__main__":
    if not os.path.exists(STATION_PATH):
        download_dataset()
        reconstruct_data()
    plot_pulseintegrals()
