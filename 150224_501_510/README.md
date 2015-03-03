501-510
=======

Use the fact that these two stations are almost ontop of each other.
This allows for interessting analysis for station performance.


## download_dataset.py

Download data. Download a dataset of individual events from each
station. And download coincidences, containing only events in
coincidence.


## reconstructions.py

Reconstruct events in coincidence.


## detector_offsets.py

Determine detector offsets from the dataset with 'all' events for each
station.


## station_offsets.py

Determine station offsets from the dataset of events in coincidence.


## coincidence_window.py

Number of coincidences as function of coincidence window. There should
be little time difference since they are at the same location, event
angles showers should arrive at the same time. Some time offset might
exist due to a GPS offset. Thickness of showerfront?


## anti_coincidences.py

Check number of particles in the detectors for events in coincidence and
events not in coincidence. Gives an indication of the detection chance
as function of particle density.


## angles.py

Compare the reconstructed zenith and azimuth for events in coincidence.
Also compare it as a function of particle density. More particles
results in better agreement. Also check for smaller coincidence windows?


## densities.py

Compare the particle counts for events in coincidence.
Compare for the adjacent detectors and for the total station count.


## test_detector_positions.py

Make plots comparing the reconstructed azimuths of the two stations,
doing this for different station layouts (i.e. swap detector locations).
If the detectors have been numbered wrong this should be easily
discovered.
