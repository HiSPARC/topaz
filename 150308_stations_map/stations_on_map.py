from numpy import array
from smopy import Map
from sapphire.api import Network, Station


def show_map():
    x = []
    y = []
    latitudes = []
    longitudes = []

    for station_number in Network().station_numbers(cluster=0):
        try:
            location = Station(station_number).location()
        except:
            continue
        if location['latitude'] == 0 or location['longitude'] == 0:
            continue
        latitudes.append(location['latitude'])
        longitudes.append(location['longitude'])

    map = Map((min(latitudes), min(longitudes), max(latitudes), max(longitudes)), z=11)
    ax = map.show_mpl(figsize=(8, 6))
    x, y = map.to_pixels(array(latitudes), array(longitudes))
    ax.plot(x, y, 'ob', ms=5)


if __name__ == '__main__':
    show_map()
