import shutil

from sapphire.corsika.qsub_corsika import *


class CorsikaRerun(CorsikaBatch):

    def __init__(self, seeds, queue='long'):
        self.seed1, self.seed2 = seeds.split('_')
        self.rundir = seeds + '/'
        self.corsika = 'corsika74000Linux_QGSII_gheisha'
        self.queue = queue

    def prepare_env(self):
        """Setup CORSIKA environment"""

        # Set umask
        os.umask(002)

        # Setup directories
        self.make_rundir()
        self.goto_rundir()

        # copy input from bad run
        self.copy_input()
        self.copy_config()

        # remove bad run
        self.remove_bad()

    def copy_input(self):
        input = 'DATDIR    /data/hisparc/corsika/corsika-74000/run/\n'
        old_path = os.path.join(DATADIR, self.rundir, 'input-hisparc')
        with open(old_path, 'r') as prev_input:
            input += prev_input.read()

        new_path = os.path.join(self.get_rundir(), 'input-hisparc')
        with open(new_path, 'w') as input_file:
            input_file.write(input)

    def remove_bad(self):
        shutil.rmtree(os.path.join(DATADIR, self.rundir))


def multiple_jobs(seeds_list, progress=True):
    """Use this to sumbit multiple jobs to Stoomboot

    :param seeds_list: List of seeds (seed1_seed2) to rerun.
    :param progress: Toggle printing of overview.

    """
    available_slots = qsub.check_queue('long')
    if available_slots <= 0 or available_slots < len(seeds_list):
        raise Exception('Submitting no jobs because selected queue is to full.')

    for seeds in pbar(seeds_list, show=progress):
        batch = CorsikaRerun(seeds)
        batch.run()


if __name__ == "__main__":
    with open('seeds_list.txt', 'r') as data:
        seeds_list = [seeds for seeds in data.read().split('\n') if seeds]
    multiple_jobs(seeds_list)
