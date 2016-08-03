# 160705 t-trigger filter

Examine the difference in reconstructed trigger time between raw unfiltered
traces and filtered traces.

The HiSPARC electronics trigger based on raw unfiltered traces received from
the ADCs. The trigger moment determines the GPS time and thus the trigger
moment in the traces needs to be reconstructed to properly align the trace
timeline with GPS time.

If the traces are filtered and sent to the datastore filtered the trigger time reconstruction sometimes fails or may reconstruct the wrong moment.

Here the trigger time will be reconstructed for unfiltered (and unreduced)
traces, then the traces will be filtered offline and trigger time reconstruction attempted again, to compare the differences.
