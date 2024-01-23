import os
from dataclasses import dataclass

import yaml

from auto_od.helper.settings import find_last_train


@dataclass
class Settings:
    mmdet_dir: str = ''
    dataset_type: str = 'CocoDataset'
    task: str = 'Object Detection'
    dataset_dir: str = ''
    train_dir: str = ''
    base_dir: str = ''
    epoch_number: int = 0

    def __post_init__(self):
        self.mmdet_config = os.path.join(self.mmdet_dir, "configs")
        self.runs_archive_dir = os.path.join(self.base_dir, "runs_archive")
        self.train_dir = find_last_train(self.runs_archive_dir)
        self.conf_dir = os.path.join(self.train_dir, 'configs')
        self.checkpoints_dir = os.path.join(self.train_dir, 'checkpoints')
        self.models_dir = os.path.join(self.train_dir, 'models')
        self.test_json = "test.json" if self.dataset_type == 'CocoDataset' else "default_test.json"
        self.train_json = "train.json" if self.dataset_type == 'CocoDataset' else "default_train.json"


def load_settings_from_yaml(file_path):
    with open(file_path, 'r') as f:
        yaml_config = yaml.safe_load(f)
        return Settings(**yaml_config)
