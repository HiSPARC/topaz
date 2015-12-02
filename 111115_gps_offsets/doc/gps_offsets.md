This is a list of a combination of tests that used the same HiSPARC box
but used a different GPS combination, giving insight in the difference
caused by that change.

Here the difference between a shared GPS signal (test-test) and each box
using its own GPS (test-501).


Difference between GPS: test-test test-501

     id                  offset     std    len
     37  050/test/PMT2   -17.97    3.24   3.98
     10  050/501/PMT2    -28.35    4.49   0.93
    diff                 -10.38

     33  018/test/PMT1   -29.63    2.91   0.83
      4  018/501/PMT2    -37.42    4.79   2.65
    diff                  -7.79


Here the difference between each box using a specific GPS (501-test) and
those GPSs swapped around (test-501).


Difference between GPS: 501-test test-501

     17  040/501/PMT2    -22.98    4.39   1.05
     18  040/test/PMT2    -6.53    4.72   0.83
    diff                 -16.45


      1  083/501/PMT2    -24.40    4.48   0.94
     19  083/test/PMT2    -6.82    4.55   2.25
    diff                 -17.58
