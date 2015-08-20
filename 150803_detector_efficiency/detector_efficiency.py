import glob
import os

from artist import Plot


def analyse():
    """Analyse results

    Determine fractions for r, zenith, and E:

    - Number of triggered showers vs total
    - Number of succesfully reconstructed showers vs total
      Succesful reconstruction: within xx degrees.
     - different combinationbs of detectors/stations
     -

    """
    station_number = 501
    for energy in [15]:
        plot = Plot()
        plot_david_data(plot)
        plot.set_ylabel('Efficiency')
        plot.set_ylimits(min=0, max=1)
        plot.set_xlimits(min=0, max=100)
        plot.set_xlabel('Core distance')
        plot.save_as_pdf('efficiency_%d_%.1f.pdf' % (station_number, energy))


def plot_david_data(plot):
    """For comparison with figure 4.6 from Fokkema2012

    Source: DIR-plot_detection_efficiency_vs_R_for_angles-1.tex

    """
    plot.plot(*zip((2.6315, 0.9995), (7.8947, 0.9947), (13.157, 0.9801),
                   (18.421, 0.9382), (23.684, 0.8653), (28.947, 0.7636),
                   (34.210, 0.6515), (39.473, 0.5313), (44.736, 0.4243),
                   (50.000, 0.3287), (55.263, 0.2467), (60.526, 0.1798),
                   (65.789, 0.1270), (71.052, 0.0898), (76.315, 0.0624),
                   (81.578, 0.0445), (86.842, 0.0301), (92.105, 0.0220),
                   (97.368, 0.0153)), linestyle='red')
    plot.plot(*zip((2.6315, 0.9642), (7.8947, 0.9242), (13.157, 0.8459),
                   (18.421, 0.7405), (23.684, 0.6224), (28.947, 0.4870),
                   (34.210, 0.3705), (39.473, 0.2668), (44.736, 0.1909),
                   (50.000, 0.1269), (55.263, 0.0833), (60.526, 0.0533),
                   (65.789, 0.0366), (71.052, 0.0243), (76.315, 0.0161),
                   (81.578, 0.0115), (86.842, 0.0079), (92.105, 0.0047),
                   (97.368, 0.0034)), linestyle='red')
    plot.plot(*zip((2.6315, 0.7180), (7.8947, 0.6214), (13.157, 0.4842),
                   (18.421, 0.3441), (23.684, 0.2296), (28.947, 0.1414),
                   (34.210, 0.0882), (39.473, 0.0513), (44.736, 0.0317),
                   (50.000, 0.0193), (55.263, 0.0109), (60.526, 0.0071),
                   (65.789, 0.0043), (71.052, 0.0029), (76.315, 0.0021),
                   (81.578, 0.0012), (86.842, 0.0009), (92.105, 0.0006),
                   (97.368, 0.0005)), linestyle='red')


if __name__ == "__main__":
#     reconstruct()
    analyse()
