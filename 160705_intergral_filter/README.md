# 160705 Intergral Filter

Examine the difference in pulse integral values between raw unfiltered traces
and filtered traces.

Filtering changes the trace values which influences the pulse integral. The
value of the integral changes only a little bit when filtering the traces. In
most cases the difference is less than 150 ADC sample. Normally the integral
based MPV is around 1000 ADC sample (2500 ADC ns). So the possible deviations
due to filtering or not filtering the traces before determining the number of
particles is only up to 15%, and usually much less.
