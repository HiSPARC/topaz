""" Reconstruct the results

"""
import tables

from sapphire import ReconstructESDEvents, ReconstructESDCoincidences


RESULT_PATH = 'result_400_gen_16394.h5'


def reconstruct_simulations():
    with tables.open_file(RESULT_PATH, 'a') as data:
        cluster = data.root.coincidences._v_attrs.cluster

        for station in cluster.stations:
            station_group = '/cluster_simulations/station_%d' % station.number
            rec_events = ReconstructESDEvents(data, station_group, station,
                                              overwrite=True, progress=True)
            rec_events.prepare_output()
            rec_events.offsets = station.detector_offsets
            rec_events.store_offsets()
            try:
                rec_events.reconstruct_directions()
                rec_events.store_reconstructions()
            except:
                pass

        rec_coins = ReconstructESDCoincidences(data, '/coincidences',
                                               overwrite=True, progress=True)
        rec_coins.prepare_output()
        rec_coins.offsets = {station.number: [o + station.gps_offset
                                              for o in station.detector_offsets]
                             for station in cluster.stations}
        try:
            rec_coins.reconstruct_directions()
            rec_coins.store_reconstructions()
        except:
            pass


if __name__ == '__main__':
    reconstruct_simulations()
