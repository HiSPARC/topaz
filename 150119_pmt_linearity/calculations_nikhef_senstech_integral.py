from __future__ import division

from numpy import mean
from artist import Plot


if __name__ == '__main__':

    led_ph = [1, 174, 228, 160, 222, 250, 263, 170, 317, 185, 230,
              240, 260, 230, 250, 290, 219, 309, 168, 220, 220,
              173, 110, 190, 170]

    led_pi = [1, 3.26, 4.12, 2.89, 3.86, 4.40, 4.82, 3.60, 5.55, 3.23, 4.39,
              3.87, 4.99, 4.20, 4.50, 4.60, 3.95, 5.56, 3.23, 3.80, 3.75,
              3.40, 2.42, 3.50, 3.68]

    multi_led = [((1, 2), 330, 6.00),
                 ((1, 2, 3), 500, 9.52),
                 ((1, 2, 3, 4), 712, 13.05),
                 ((1, 2, 3, 4, 5), 955, 18.89),
                 ((1, 2, 3, 4, 5, 6, 7), 1420, 26.61),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9), 1880, 35.84),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), 2331, 43.15),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), 2825, 53.20),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), 3340, 61.20),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), 3838, 77.48),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 4183, 84.74),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21), 4549, 90.00),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), 4831, 95.73),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4971, 99.48)]

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
    graph.save_as_pdf('linearity_nikhef_senstech_ph')

    graph = Plot()
    graph.scatter(sum_signals_pi, signals_pi)
    graph.plot([0, 100], [0, 100], mark=None)
    graph.set_xlabel('Sum individual LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseintegrals [nVs]')
    graph.save_as_pdf('linearity_nikhef_senstech_pi')

    graph = Plot()
    graph.scatter(signals_pi, signals_ph)
    graph.scatter(led_pi[1:], led_ph[1:])
    graph.plot([0, 5500 * ratio], [0, 5500], mark=None)
    graph.set_xlabel('Multiple-LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseheights [mV]')
    graph.save_as_pdf('linearity_nikhef_senstech_ph_pi')
