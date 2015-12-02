"""Width of dt distribution vs distance

Fokkema 2012 and Bosboom 2011 found that 1 ns / m fits the data.
For me 1.1 ns / m seems a better fit (not actually fitted).

    502  91   100
    503  139  139
    504  272  292
    505  233  265
    506  158  169
    508  54   55
    509  354  412
    510  2    8

"""

from artist import Plot


def plot_distance_width():
    plot = Plot()
    d = [91, 139, 272, 233, 158, 54, 354, 2]
    s = [100, 138, 292, 265, 169, 55, 412, 8]
    plot.scatter(d, s)
    plot.plot([0, 400], [0, 440], mark=None)
    plot.set_xlabel('Distance')
    plot.set_ylabel('Width of dt distribution')
    plot.save_as_pdf('plots/distance_v_width')


if __name__ == "__main__":
    plot_distance_width()
