import os

import torch
from mmdet.utils import setup_cache_size_limit_of_dynamo
from mmengine.config import Config
from mmengine.registry import RUNNERS
from mmengine.runner import Runner

from auto_od.core.settings import load_settings_from_yaml

DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'


class DetectorTrainer:
    def __init__(self,
                 config_path,
                 settings_path: str,
                 amp=False,
                 auto_scale_lr=False,  # scale lr with gpu's number
                 resume=None,
                 cfg_options=None,
                 launcher='none',
                 local_rank=0,
                 set_random_seed=None):
        self.config = load_settings_from_yaml(settings_path)
        self.config_path = config_path
        self.amp = amp
        self.auto_scale_lr = auto_scale_lr
        self.resume = resume
        self.cfg_options = cfg_options
        self.launcher = launcher
        self.local_rank = local_rank
        self.set_random_seed = set_random_seed

    def folder_saved_model(self):
        if not os.path.exists(self.config.models_dir):
            os.makedirs(self.config.models_dir)

    def setup_cache(self):
        setup_cache_size_limit_of_dynamo()

    def load_config(self):
        cfg = Config.fromfile(self.config_path)
        cfg.launcher = self.launcher
        if self.cfg_options is not None:
            cfg.merge_from_dict(self.cfg_options)

        if self.set_random_seed is not None:
            cfg.randomness = dict(seed=self.set_random_seed)
            cfg.randomness.deterministic = True

        cfg.work_dir = self.config.models_dir

        if self.amp:
            optim_wrapper = cfg.optim_wrapper.type
            if optim_wrapper != 'AmpOptimWrapper':
                assert optim_wrapper == 'OptimWrapper', (
                    '`--amp` is only supported when the optimizer wrapper type is '
                    f'`OptimWrapper` but got {optim_wrapper}.')
                cfg.optim_wrapper.type = 'AmpOptimWrapper'
                cfg.optim_wrapper.loss_scale = 'dynamic'

        if self.auto_scale_lr:
            if cfg.get('auto_scale_lr', {}).get('enable') and 'base_batch_size' in cfg.auto_scale_lr:
                cfg.auto_scale_lr.enable = True
        #     error handler

        cfg.resume, cfg.load_from = (True, None) if self.resume == 'auto' \
            else (True, self.resume) if self.resume is not None \
            else (False, None)
        return cfg

    def train(self):
        self.setup_cache()
        cfg = self.load_config()

        if 'runner_type' not in cfg:
            runner = Runner.from_cfg(cfg)
        else:
            runner = RUNNERS.build(cfg)

        runner.train()


