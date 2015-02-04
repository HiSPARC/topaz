from __future__ import division

from numpy import mean
from artist import Plot


if __name__ == '__main__':

    led_ph = [1, 140, 170, 145, 225, 224, 222, 146]

    led_pi = [1, 2.17, 2.60, 2.22, 3.13, 3.33, 3.40, 2.65]

    multi_led = [((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4590, 73.39),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 3820, 59.60),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), 3100, 48.90),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9), 1730, 26.00),
                 ((1, 2, 3, 4, 5, 6), 1090, 17.16),
                 ((1, 2, 3, 4), 664, 10.62),
                 ((1, 2), 320, 5.05)]

    signals_ph = [ph for fibers, ph, pi in multi_led]
    signals_pi = [pi for fibers, ph, pi in multi_led]

    ratio = mean([pi / ph for ph, pi in zip(led_ph[1:], led_pi[1:])])

    graph = Plot()
    graph.scatter(signals_pi, signals_ph)
    graph.scatter(led_pi[1:], led_ph[1:])
    graph.plot([0, 5500 * ratio], [0, 5500], mark=None)
    graph.set_xlabel('Multiple-LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseheights [mV]')
    graph.save_as_pdf('linearity_nikhef_ph_pi')
