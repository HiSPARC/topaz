""" Get the HiSPARC firmware version for each station."""

try:
    from django_publicdb.histograms.models import Configuration
    from django_publicdb.inforecords.models import Station

    DJANGO = True
except ImportError:
    from sapphire import Station, Network

    DJANGO = False


def get_versions_django():
    stations = Station.objects.all()
    for station in stations:
        try:
            config = Configuration.objects.filter(source__station=station).latest('timestamp')
            print('% 5d' % station.number, config.mas_version)
        except:
            print('% 5d' % station.number, '--')


def get_versions_api():
    station_numbers = Network().station_numbers()
    for station_number in station_numbers:
        config = Station(station_number).config()
        print('% 5d' % station_number, config['mas_version'])


if __name__ == '__main__':
    if DJANGO:
        get_versions_django()
    else:
        get_versions_api()

# Found some with old versions:
#
# 6 Hardware: 55    FPGA: 11
# 202 Hardware: 97    FPGA: 11
# 601 Hardware: 48    FPGA: 10
# 1001 Hardware: 79    FPGA: 11
# 1002 Hardware: 99    FPGA: 11
# 1003 Hardware: 99    FPGA: 11
# 1008 Hardware: 53    FPGA: 11
# 1099 Hardware: 28    FPGA: 11
# 2002 Hardware: 87    FPGA: 11
# 7201 Hardware: 96    FPGA: 11
# 7401 Hardware: 64    FPGA: 11
# 8104 Hardware: 92    FPGA: 11
# 11001 Hardware: 46    FPGA: 10
# 12001 Hardware: 68    FPGA: 10
