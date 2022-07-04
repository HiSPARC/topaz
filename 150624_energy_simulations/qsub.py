import textwrap

from sapphire import qsub


SCRIPT_TEMPLATE = textwrap.dedent("""\
    #!/usr/bin/env bash
    umask 002
    source activate /data/hisparc/corsika_env &> /dev/null
    cd /data/hisparc/adelaat/science_park_corsika
    mkdir {seed}
    cd {seed}
    ln -s /data/hisparc/corsika/data/{seed}/corsika.h5 corsika.h5
    python ../run.py
    # To alleviate Stoomboot, make sure the job is not to short.
    sleep $[ ( $RANDOM % 60 ) + 60 ]""")


def submit_job(seed):
    """Submit job to Stoomboot"""

    script = SCRIPT_TEMPLATE.format(seed=seed)
    name = f'spa_sim_{seed}'

    qsub.submit_job(script, name, queue='long')


if __name__ == "__main__":
    with open('seed_list.txt') as seed_list:
        seeds = seed_list.read().split('\n')

    for seed in seeds:
        if not seed == '':
            submit_job(seed)
