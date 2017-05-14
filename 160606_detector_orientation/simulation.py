"""Compare azimuthal detection effciciency for station layout

Compare trigger efficiency for 2-detector stations for inclined showers as
function of detector orientation relative to detector placement for different
shower azimuth angles. Also check the effect of using square detectors in the
general simulation, does it greatly affect efficiency?

"""
import os

import numpy as np
import tables

from artist import MultiPlot, Plot

from sapphire.clusters import BaseCluster
from sapphire.simulations.detector import ErrorlessSimulation
from sapphire.simulations.groundparticles import DetectorBoundarySimulation

CORSIKA_DATA_e15_z375 = '/Users/arne/Datastore/CORSIKA/312356151_602799693/corsika.h5'
RESULT_DATA = '/Users/arne/Datastore/detector_orientation/sim.h5'


def ThreeStationsOrientation(d=10):

    cluster = BaseCluster()
    for i, orientation in enumerate(['UD', 'LR', 'UD']):
        detectors = [((-d / 2., 0, 0), orientation),
                     ((d / 2., 0, 0), orientation)]
        cluster._add_station((0, 0, 0), 0, detectors, number=i)
        if i == 2:
            for d in cluster.stations[-1].detectors:
                d._detector_size = (np.sqrt(0.5), np.sqrt(0.5))
    return cluster


class ErrorlessDetectorBoundarySimulation(ErrorlessSimulation,
                                          DetectorBoundarySimulation):

    pass


def do_simulation():
    with tables.open_file(RESULT_DATA, 'a') as data:
        cluster = ThreeStationsOrientation()
        sim = ErrorlessDetectorBoundarySimulation(CORSIKA_DATA_e15_z375, 150,
                                                  cluster, data, N=30000,
                                                  progress=True,
                                                  output_path='/')
        sim.run()

        cluster = ThreeStationsOrientation(5)
        sim = ErrorlessDetectorBoundarySimulation(CORSIKA_DATA_e15_z375, 150,
                                                  cluster, data, N=30000,
                                                  progress=True,
                                                  output_path='/d5')
        sim.run()


def plot_n_azimuth(path='/'):
    with tables.open_file(RESULT_DATA, 'r') as data:
        coin = data.get_node(path + 'coincidences/coincidences')
        in_azi = coin.col('azimuth')
        ud_azi = coin.read_where('s0', field='azimuth')
        lr_azi = coin.read_where('s1', field='azimuth')
        sq_azi = coin.read_where('s2', field='azimuth')
        udlr_azi = coin.get_where_list('s0 & s1')
        print ('Percentage detected in both %f ' %
               (float(len(udlr_azi)) / len(in_azi)))

        bins = np.linspace(-np.pi, np.pi, 30)
        in_counts = np.histogram(in_azi, bins)[0].astype(float)
        ud_counts = np.histogram(ud_azi, bins)[0].astype(float)
        lr_counts = np.histogram(lr_azi, bins)[0].astype(float)
        sq_counts = np.histogram(sq_azi, bins)[0].astype(float)

        print ('Detected: UD %d | LR %d | SQ %d' %
               (sum(ud_counts), sum(lr_counts), sum(sq_counts)))

        plot = Plot()
        plot.histogram(ud_counts / in_counts, bins, linestyle='black')
        plot.histogram(lr_counts / in_counts, bins + 0.01, linestyle='red')
        plot.histogram(sq_counts / in_counts, bins + 0.01, linestyle='blue')
        plot.histogram((ud_counts - lr_counts) / in_counts, bins, linestyle='black')
        plot.set_xlabel(r'Shower azimuth [\si{\radian}]')
        plot.set_ylabel(r'Percentage detected')
        plot.set_xlimits(bins[0], bins[-1])
        plot.draw_horizontal_line(0, linestyle='thin, gray')
#         plot.set_ylimits(0)
        plot.save_as_pdf('azimuth_percentage' + path.replace('/', '_'))


def plot_n_histogram(path='/'):
    with tables.open_file(RESULT_DATA, 'r') as data:
        sims = data.get_node(path + 'cluster_simulations')
        ud_n1 = sims.station_0.events.col('n1')
        ud_n2 = sims.station_0.events.col('n2')
        lr_n1 = sims.station_1.events.col('n1')
        lr_n2 = sims.station_1.events.col('n2')

        bins = np.linspace(0, 80, 40)
        ud_counts1, _ = np.histogram(ud_n1, bins)
        ud_counts2, _ = np.histogram(ud_n2, bins)
        lr_counts1, _ = np.histogram(lr_n1, bins)
        lr_counts2, _ = np.histogram(lr_n2, bins)

        plot = Plot()
        plot.histogram(ud_counts1, bins, linestyle='black')
        plot.histogram(ud_counts2, bins, linestyle='red')
        plot.histogram(lr_counts1, bins + 0.01, linestyle='black, dashed')
        plot.histogram(lr_counts2, bins + 0.01, linestyle='red, dashed')
        plot.set_xlabel(r'Number of detected particles')
        plot.set_ylabel(r'Number of events with n detected')
        plot.set_xlimits(bins[0], bins[-1])
        plot.set_ylimits(0)
        plot.save_as_pdf('n_histogram' + path.replace('/', '_'))


def plot_detector_dt(path='/'):
    with tables.open_file(RESULT_DATA, 'r') as data:
        sims = data.get_node(path + 'cluster_simulations')
        ud_dt = sims.station_0.events.col('t1') - sims.station_0.events.col('t2')
        lr_dt = sims.station_1.events.col('t1') - sims.station_1.events.col('t2')

        bins = np.linspace(-61.25, 61.25, 50)
        ud_counts, _ = np.histogram(ud_dt, bins)
        lr_counts, _ = np.histogram(lr_dt, bins)

        plot = Plot()
        plot.histogram(ud_counts, bins, linestyle='black')
        plot.histogram(lr_counts, bins, linestyle='red')
        plot.set_xlabel(r'Time difference [\si{\ns}]')
        plot.set_ylabel(r'Number events with time difference')
        plot.set_xlimits(bins[0], bins[-1])
        plot.set_ylimits(0)
        plot.save_as_pdf('dt' + path.replace('/', '_'))


def plot_layouts(path='/'):
    with tables.open_file(RESULT_DATA, 'r') as data:
        cluster = data.get_node_attr(path + 'coincidences', 'cluster')
        plot = MultiPlot(3, 1, width=r'0.67\textwidth', height=r'.2\textwidth')
        for splot, station in zip(plot.subplots, cluster.stations):
            for detector in station.detectors:
                x, y = zip(*detector.get_corners())
                splot.plot(x + x[:1], y + y[:1], mark=None)
                splot.set_axis_equal()
        plot.show_xticklabels_for_all([(2, 0)])
        plot.show_yticklabels_for_all()
        plot.set_ylabel(r'North [\si{\meter}]')
        plot.set_xlabel(r'East [\si{\meter}]')
        plot.set_xlimits_for_all(None, -6, 6)
        plot.set_ylimits_for_all(None, -1.2, 1.2)
        plot.save_as_pdf('layouts' + path.replace('/', '_'))


if __name__ == "__main__":
    if not os.path.exists(RESULT_DATA):
        do_simulation()
    plot_n_azimuth()
    plot_n_histogram()
    plot_detector_dt()
    plot_layouts()

    path = '/d5/'
    plot_n_azimuth(path)
    plot_n_histogram(path)
    plot_detector_dt(path)
    plot_layouts(path)
