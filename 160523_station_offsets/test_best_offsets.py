from pprint import PrettyPrinter
from random import sample

from sapphire import HiSPARCStations, Station
from sapphire.analysis.direction_reconstruction import CoincidenceDirectionReconstruction

# SN = [501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511]
SN = [501, 502, 503, 505, 506, 508, 510, 511]
cluster = HiSPARCStations(SN, force_stale=True)
crec = CoincidenceDirectionReconstruction(cluster)
offsets = {sn: Station(sn, force_stale=True) for sn in SN}

ref_sn = 501
station_number = 502

ts0 = 1461542400

print crec.determine_best_offsets(SN, ts0, offsets)
print offsets[station_number].station_timing_offset(ref_sn, ts0)
print offsets[station_number].detector_timing_offset(ts0)

offs = crec.determine_best_offsets([sn for sn in sample(SN, len(SN))], ts0, offsets)
reference = offs[ref_sn][1]
offs = {sn: round(off[1] - reference, 1) for sn, off in offs.items()}
pp = PrettyPrinter()
pp.pprint(offs)
