from urllib2 import urlopen
from json import loads
from datetime import date, timedelta
from pylab import imshow, show, yticks, savefig

def main():
    api = loads(urlopen("http://data.hisparc.nl/api/").read())
    base_subclusters = ''.join([api['base_url'], api['stations_in_subcluster']])
    base_clusters = ''.join([api['base_url'], api['subclusters_in_cluster']])
    base_countries = ''.join([api['base_url'], api['clusters_in_country']])
    base_world = ''.join([api['base_url'], api['countries']])

    years = arange(2004, 2014)
    months = arange(12)

    countries = loads(urlopen(base_world).read())

    clusters = []
    for country in countries:
        clusters_url = base_countries.format(country_id=country['number'])
        clusters.extend(loads(urlopen(clusters_url).read()))

    subclusters = []
    for cluster in clusters:
        subclusters_url = base_clusters.format(cluster_id=cluster['number'])
        subclusters.extend(loads(urlopen(subclusters_url).read()))

    stations = []
    for subcluster in subclusters:
        stations_url = base_subclusters.format(subcluster_id=subcluster['number'])
        stations.extend(loads(urlopen(stations_url).read()))

    data = []

    for station in stations:
        id = station['number']
        base_num = 'http://data.hisparc.nl/api/station/%d/num_events/%d/%d/'
        events = []
        for curr_year in years:
            for curr_month in months:
                if curr_year == 2013 and curr_month >= 7:
                    continue
                url = urlopen(base_num % (id, curr_year, (curr_month % 12) + 1))
                events.append(int(url.read()))
        data.append(events)
        print 'got data for %d' % station['number']

    figure(figsize=(16, 11), facecolor='none', edgecolor='none')
    imshow(data, interpolation='nearest', cmap=plt.get_cmap('Greys'), vmin=0, vmax=2e6)

    station_ids = [station['number'] for station in stations]
    yticks(arange(len(station_ids)), station_ids, size='xx-small')
    xticks((years - years[0]) * 12, years, size='xx-small')
    title("Number of events per month between 2004 and 2013, scale: 0-2e6")

    savefig('/tmp/all_station_n_events_month.pdf',
            facecolor='none', edgecolor='none')


if __name__=="__main__":
    main()
