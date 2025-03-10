import shutil
from pathlib import Path

from mmvae_hub import log
from mmvae_hub.utils.setup.flags_utils import get_config_path
from mmvae_hub.utils.utils import json2dict


def compress_experiment_run_dir(flags) -> None:
    """
    Move zipped experiment_dir_run in TMPDIR to experiment_dir.
    """
    dir_experiment = Path(json2dict(get_config_path(flags=flags))['dir_experiment']).expanduser()
    dir_experiment.mkdir(exist_ok=True)

    # zip dir_experiment_run
    log.info(f'zipping {flags.dir_experiment_run} '
             f'to {(Path(dir_experiment) / flags.experiment_uid).with_suffix(".zip")}.')
    dir_experiment_zipped = (dir_experiment / flags.experiment_uid)

    shutil.make_archive(dir_experiment_zipped, 'zip', flags.dir_experiment_run, verbose=True)

    assert dir_experiment_zipped.with_suffix('.zip').exists(), f'{dir_experiment_zipped} does not exist. ' \
                                                               f'Zipping of dir_experiment_run failed.'
    # delete not compressed experiment dir
    shutil.rmtree(str(flags.dir_experiment_run))
