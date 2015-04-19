from __future__ import division

from numpy import mean


def get_measured_expected(led_ph, led_pi, multi_led):
    """

    :param led_ph: individual fiber measurements of pulseheight
    :param led_pi: individual fiber measurements of pulseintegral
    :param multi_led: tuple of fibers numbers, measured pulseheight
                      and pulseintegral

    """
    measured_pi = []
    measured_ph = []
    expected_pi = []
    expected_ph = []
    for fibers, ph, pi in multi_led:
        measured_ph.append(ph)
        measured_pi.append(pi)
        expected_ph.append(sum(led_ph[fiber] for fiber in fibers))
        expected_pi.append(sum(led_pi[fiber] for fiber in fibers))

    return measured_pi, measured_ph, expected_pi, expected_ph

def determine_pi_ph_ratio(led_pi, led_ph):
    """Calculate ratio between pulseintegral and pulseheight

    :param led_ph: individual fiber measurements of pulseheight
    :param led_pi: individual fiber measurements of pulseintegral

    """
    ratio = mean([pi / ph for ph, pi in zip(led_ph[1:], led_pi[1:])
                  if not (pi == 0. or ph == 0.)])
    return ratio
