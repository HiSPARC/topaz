from __future__ import division

from numpy import mean
from artist import Plot


if __name__ == '__main__':

    led_ph = [1, 150, 220, 156, 225, 230, 230, 182, 299, 163, 202,
              220, 250, 202, 244, 240, 190, 240, 159, 196, 180,
              182, 160, 210, 202]

    led_pi = [1, 1.68, 2.44, 1.80, 2.43, 2.56, 2.57, 2.18, 3.32, 1.82, 2.46,
              2.46, 3.00, 2.36, 2.87, 2.56, 2.22, 2.79, 1.84, 2.20, 2.05,
              2.00, 1.83, 2.47, 2.70]

    multi_led = [((23, 24), 325, 4.45),
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

    signals_ph = [ph for fibers, ph, pi in multi_led]
    signals_pi = [pi for fibers, ph, pi in multi_led]
    sum_signals_ph = [sum(led_ph[fiber] for fiber in fibers) for fibers, ph, pi in multi_led]
    sum_signals_pi = [sum(led_pi[fiber] for fiber in fibers) for fibers, ph, pi in multi_led]

    ratio = mean([pi/ph for ph, pi in zip(led_ph[1:], led_pi[1:])])

    graph = Plot()
    graph.scatter(sum_signals_ph, signals_ph)
    graph.plot([0, 5500], [0, 5500], mark=None)
    graph.set_xlabel('Sum individual LED pulseheights [mV]')
    graph.set_ylabel('Multiple-LED pulseheight [mV]')
    graph.save_as_pdf('linearity_senstech_ph')

    graph = Plot()
    graph.scatter(sum_signals_pi, signals_pi)
    graph.plot([0, 100], [0, 100], mark=None)
    graph.set_xlabel('Sum individual LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseintegrals [nVs]')
    graph.save_as_pdf('linearity_senstech_pi')

    graph = Plot()
    graph.scatter(signals_pi, signals_ph)
    graph.scatter(led_pi[1:], led_ph[1:])
    graph.plot([0, 5500 * ratio], [0, 5500], mark=None)
    graph.set_xlabel('Multiple-LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseheights [mV]')
    graph.save_as_pdf('linearity_senstech_ph_pi')
