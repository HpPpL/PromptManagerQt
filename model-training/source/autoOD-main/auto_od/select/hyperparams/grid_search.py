import os
from itertools import product

from mmdet.registry import RUNNERS
from mmdet.utils import setup_cache_size_limit_of_dynamo
from mmengine import Config
from mmengine.runner import Runner

from auto_od.train.trainer import DetectorTrainer


class GridSearch:
    def __init__(self, settings_path: str, base_config_path, search_space):
        self.base_config_path = base_config_path
        self.search_space = search_space
        self.settings_path = settings_path

    @staticmethod
    def get_latest_checkpoint(checkpoint_dir):
        """Get the most recently modified checkpoint file from a directory."""
        checkpoint_files = [os.path.join(checkpoint_dir, f) for f in os.listdir(checkpoint_dir) if f.endswith('.pth')]
        if not checkpoint_files:
            raise FileNotFoundError(f"No checkpoint files found in {checkpoint_dir}")
        latest_checkpoint = max(checkpoint_files, key=os.path.getmtime)
        return latest_checkpoint

    @staticmethod
    def evaluate_model(cfg, checkpoint_path):
        setup_cache_size_limit_of_dynamo()
        cfg.load_from = checkpoint_path

        if 'runner_type' not in cfg:
            runner = Runner.from_cfg(cfg)
        else:
            runner = RUNNERS.build(cfg)

        results = runner.test()
        print("results = ", results)

        performance_metric = results["coco/bbox_mAP"]
        return performance_metric

    def train_and_evaluate(self, cfg_options, checkpoint_dir):
        cfg = Config.fromfile(self.base_config_path)
        for key, value in cfg_options.items():
            key_parts = key.split('.')
            d = cfg
            for part in key_parts[:-1]:
                d = d[part]
            d[key_parts[-1]] = value

        trainer = DetectorTrainer(settings_path=self.settings_path, config_path=self.base_config_path, cfg_options=cfg_options)
        trainer.train()

        checkpoint_path = self.get_latest_checkpoint(checkpoint_dir)

        return self.evaluate_model(cfg, checkpoint_path)

    def grid_search(self, checkpoint_dir):
        best_performance = None
        best_config_options = None

        for combination in product(*self.search_space.values()):
            cfg_options = dict(zip(self.search_space.keys(), combination))
            print(f"Training with configuration: {cfg_options}")

            performance = self.train_and_evaluate(cfg_options, checkpoint_dir)

            if best_performance is None or performance > best_performance:
                best_performance = performance
                best_config_options = cfg_options

            print(f"Combination: {cfg_options}, Performance: {performance}")

        return best_config_options, best_performance



