from __future__ import division

from numpy import mean
from artist import Plot


if __name__ == '__main__':

    nled_ph = [1, 155, 193, 155, 219, 233, 239, 169, 322, 160, 230,
               240, 285, 208, 222, 262, 174, 319, 168, 210, 216,
               162, 130, 213, 166]

    nled_pi = [1, 2.43, 3.15, 2.48, 3.18, 3.60, 3.70, 2.72, 5.09, 2.49, 3.66,
               3.57, 4.51, 3.15, 3.49, 3.81, 2.64, 4.93, 2.72, 3.13, 3.27,
               2.55, 2.07, 3.40, 2.93]

    nmulti_led = [((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 5050, 86.50),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22), 4723, 73.61),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20), 4396, 68.58),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), 3950, 61.43),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 3560, 55.46),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), 3150, 49.00),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2686, 42.50),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2140, 34.34),
                  ((1, 2, 3, 4, 5, 6, 7, 8), 1746, 28.13),
                  ((1, 2, 3, 4, 5, 6), 1224, 20.36),
                  ((1, 2, 3, 4), 716, 11.43),
                  ((1, 2), 318, 5.00)]

    sled_ph = [1, 150, 220, 156, 225, 230, 230, 182, 299, 163, 202,
               220, 250, 202, 244, 240, 190, 240, 159, 196, 180,
               182, 160, 210, 202]

    sled_pi = [1, 1.68, 2.44, 1.80, 2.43, 2.56, 2.57, 2.18, 3.32, 1.82, 2.46,
               2.46, 3.00, 2.36, 2.87, 2.56, 2.22, 2.79, 1.84, 2.20, 2.05,
               2.00, 1.83, 2.47, 2.70]

    smulti_led = [((23, 24), 325, 4.45),
                  ((22, 23, 24), 550, 6.55),
                  ((21, 22, 23, 24), 730, 8.61),
                  ((20, 21, 22, 23, 24), 860, 10.60),
                  ((19, 20, 21, 22, 23, 24), 1000, 12.21),
                  ((18, 19, 20, 21, 22, 23, 24), 1120, 15.20),
                  ((17, 18, 19, 20, 21, 22, 23, 24), 1267, 17.66),
                  ((16, 17, 18, 19, 20, 21, 22, 23, 24), 1339, 19.12),
                  ((15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1453, 21.00),
                  ((14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1545, 23.00),
                  ((13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1605, 24.33),
                  ((12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1712, 26.55),
                  ((11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1776, 28.04),
                  ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1844, 29.46),
                  ((9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1877, 30.66),
                  ((8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1960, 32.23),
                  ((7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1983, 33.15),
                  ((6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2036, 34.30),
                  ((4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2097, 36.25),
                  ((2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2150, 38.15),
                  ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2170, 38.57)]

    nsignals_ph = [ph for fibers, ph, pi in nmulti_led]
    nsum_signals_ph = [sum(nled_ph[fiber] for fiber in fibers) for fibers, ph, pi in nmulti_led]
    nsignals_pi = [pi for fibers, ph, pi in nmulti_led]
    nsum_signals_pi = [sum(nled_pi[fiber] for fiber in fibers) for fibers, ph, pi in nmulti_led]

    ssignals_ph = [ph for fibers, ph, pi in smulti_led]
    ssum_signals_ph = [sum(sled_ph[fiber] for fiber in fibers) for fibers, ph, pi in smulti_led]
    ssignals_pi = [pi for fibers, ph, pi in smulti_led]
    ssum_signals_pi = [sum(sled_pi[fiber] for fiber in fibers) for fibers, ph, pi in smulti_led]

    graph = Plot()
    graph.scatter(nsum_signals_ph, nsignals_ph, mark='*')
    graph.scatter(ssum_signals_ph, ssignals_ph)
    graph.plot([0, 5500], [0, 5500], mark=None, linestyle='gray')
    graph.set_xlabel(r'Sum individual LED pulseheights [\si{\milli\volt}]')
    graph.set_ylabel(r'Multiple-LED pulseheight [\si{\milli\volt}]')
    graph.set_xlimits(0, 5500)
    graph.set_ylimits(0, 5500)
    graph.save_as_pdf('linearity_pmts_ph')

    graph = Plot()
    graph.scatter(nsum_signals_pi, nsignals_pi, mark='*')
    graph.scatter(ssum_signals_pi, ssignals_pi)
    graph.plot([0, 100], [0, 100], mark=None, linestyle='gray')
    graph.set_xlabel(r'Sum individual LED pulseintegrals [\si{n\volt\second}]')
    graph.set_ylabel(r'Multiple-LED pulseintegrals [\si{n\volt\second}]')
    graph.set_xlimits(0, 100)
    graph.set_ylimits(0, 100)
    graph.save_as_pdf('linearity_pmts_pi')
