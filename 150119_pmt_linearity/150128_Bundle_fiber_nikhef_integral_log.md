# PMT linearity bundle cap log


Setup
-----

Test on 2015/1/29

Nikhef PMT with Hamamatsu tube.

PMT voltage 789 V.

Bundle of many fibers in custom drilled cap.

Now performed with a different scope that can measure the pulse integral.

Oscilloscope LeCroy 434:
Acquire     Average 100
Measure     Ch1 Pk-Pk
Measure     Ch1 Area
Trigger     Ch4


Check combination of LED and Bundle fibers
------------------------------------------

    LED + Bundle Fiber    Pulseheight [mV]  Integral [nVs]
    #01                   140               2.17
    #02                   170               2.60
    #03                   145               2.22
    #04                   225               3.13
    #05                   224               3.33
    #06                   222               3.40
    #07                   146               2.65


Multiple fibers combined
------------------------

Connected multiple fibers simultaneously to add signals.

LED fibers are connected to the Bundle fiber of the same number.

    Fibers                                                          Pulseheight [mV]    Integral [nVs]
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24  4590                73.39
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19                 3820                59.60
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15                             3100                48.90
    1 2 3 4 5 6 7 8 9                                               1730                26.00
    1 2 3 4 5 6                                                     1090                17.16
    1 2 3 4                                                         664                 10.62
    1 2                                                             320                 5.05
