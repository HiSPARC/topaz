# PMT linearity bundle cap log


Setup
-----

Test on 2015/1/23

Sens Tech PMT with SN 30449.

The PMT was part of the new PMT test with station 99 as channel 2 on
2015/1/12. Good MIP peak was found at 799 V, but a test with fiber 8
showed it needed 893 V to get a similar response to the new PMT, a
signal around 356 mV.

PMT voltage 893 V.

Bundle of many fibers in custom drilled cap.

Oscilloscope:
Acquire     Average 128
Measure     Ch1 Pk-Pk
Trigger     EXT



Check combination of LED and Bundle fibers
------------------------------------------

    LED Fiber   Bundle Fiber    Pulseheight
    #01         #01             160 mV
    #02         #02             224 mV
    #03         #03             172 mV
    #04         #04             206 mV
    #05         #05             246 mV
    #06         #06             242 mV
    #07         #07             188 mV
    #08         #08             352 mV
    #09         #09             180 mV
    #10         #10             232 mV
    #11         #11             236 mV
    #12         #12             292 mV
    #13         #13             232 mV
    #14         #14             260 mV
    #15         #15             258 mV
    #16         #16             198 mV
    #17         #17             302 mV
    #18         #18             202 mV
    #19         #19             212 mV
    #20         #20             218 mV
    #21         #21             186 mV
    #22         #22             166 mV
    #23         #23             214 mV
    #24         #24             214 mV


Multiple fibers combined
------------------------

Connected multiple fibers simultaneously to add signals.

LED fibers are connected to the Bundle fiber of the same number.

    Fibers                                                          Pulseheight
    1 2                                                             344
    1 2 3                                                           536
    1 2 3 4                                                         720
    1 2 3 4 5                                                       920
    1 2 3 4 5 6                                                     1140
    1 2 3 4 5 6 7                                                   1250
    1 2 3 4 5 6 7 8                                                 1420
    1 2 3 4 5 6 7 8 9                                               1460
    1 2 3 4 5 6 7 8                                                 1400
    2 3 4 5 6 7 8                                                   1340
    3 4 5 6 7 8                                                     1240
    4 5 6 7 8                                                       1140
    1 2 3 4 5 6 7 8 9 10                                            1540
    1 2 3 4 5 6 7 8 9 10 11                                         1620
    1 2 3 4 5 6 7 8 9 10 11 12                                      1700
    1 2 3 4 5 6 7 8 9 10 11 12 13                                   1760
    1 2 3 4 5 6 7 8 9 10 11 12 13 14                                1840
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15                             1880
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16                          1920
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17                       1980
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18                    2020
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19                 2060
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20              2080
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21           2120
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22        2140
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23     2160
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24  2180
    2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24    2160
    3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24      2140
    6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24            2060
    8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24                1980
    10 11 12 13 14 15 16 17 18 19 20 21 22 23 24                    1860
    10 11 12 13 14 15 16 17 18 19 20 21 22                          1760
    10 11 12 13 14 15 16 17 18 19 20                                1680
    10 11 12 13 14 15 16                                            1350
    10 11 12 13 14                                                  1110
    10 11 12 13                                                     936
    10 11 12                                                        760
    10 11                                                           448
    7 8 9                                                           672
    6 7 8 9                                                         896
    5 6 7 8 9                                                       1070
    4 5 6 7 8 9                                                     1220
    3 4 5 6 7 8 9                                                   1290
    2 3 4 5 6 7 8 9                                                 1380
