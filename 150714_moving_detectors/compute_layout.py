from sapphire.clusters import HiSPARCStations
from sapphire.transformations.axes import cartesian_to_compass
from sapphire.transformations.clock import gps_to_datetime


STATION = 501
# Select the timestamp with the correct GPS location,
# relative to the existing station layout.
GOOD_GPS = 1412347557
OTHER_GPS = 1414406502

if __name__ == "__main__":
    cluster = HiSPARCStations([STATION])
    station = cluster.get_station(STATION)

    # Move detectors of the 'bad' location to the correct and get the new
    # relative coordinates.
    cluster.set_timestamp(GOOD_GPS)
    x0, y0 = station.get_xy_coordinates()
    cluster.set_timestamp(OTHER_GPS)
    x1, y1 = station.get_xy_coordinates()

    dx = x1 - x0
    dy = y1 - y0
    print dx, dy

    for d in station.detectors:
        cluster.set_timestamp(other_gps)
        d.x[d.index] -= dx
        d.y[d.index] -= dy
        print gps_to_datetime(OTHER_GPS)
        print cartesian_to_compass(d.x[d.index], d.y[d.index], d.z[d.index])
