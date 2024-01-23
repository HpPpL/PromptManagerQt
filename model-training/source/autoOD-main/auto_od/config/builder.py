import json
import os
from typing import Any, Tuple

from mmengine import Config

import auto_od.core.settings as s
from auto_od.core.logger import Logger


class ModelConfig:
    def __init__(self, settings_path: str, config_path: str = None, load_from_link: str = None):
        """
        Initialize ModelConfig instance.

        Args:
            config_path (str, optional): Path to the configuration file. Defaults to None.
            load_from_link (str, optional): Path to load from. Defaults to None.
        """
        self.config_path = config_path
        self.load_from_link = load_from_link

        self.config = s.load_settings_from_yaml(settings_path)
        self.logger = Logger(self.config.base_dir)

        self.full_config_path = self._extract_config_name()
        self.load_from = self._extract_load_from()

    def _extract_config_name(self) -> str:
        """
        Extracts the configuration name based on conditions.

        Returns:
            str: Full path to the configuration file. Ex. 'configs/faster_rcnn/faster-rcnn_r50_fpn_1x_coco.py'
        """
        if self.config_path is None:
            print("traindir", self.config.train_dir)
            filename = os.path.join(str(self.config.train_dir), 'paths.txt')
            with open(filename, 'r') as file:
                file_contents = file.read()

            elements = file_contents.strip('()').split(', ')
            filename = elements[1].strip("'")
            class_name = self.__class__.__name__
            function_name = ModelConfig._extract_config_name.__name__
            self.logger.call(class_name,
                             function_name,
                             additional_info="_extract_config_name: {0}".format(os.path.join(self.config.mmdet_dir,
                                                                                             filename)))
            return os.path.join(self.config.mmdet_dir, filename)
        return os.path.join(self.config.mmdet_dir, self.config_path)

    def _extract_load_from(self) -> str:
        """
        Extracts the load_from value based on conditions.

        Returns:
            str: Full path to the load_from value. Ex. '/root/project/runs_archive/train1/checkpoints/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth'
        """
        if self.load_from_link is None:
            filename = os.path.join(self.config.train_dir, 'paths.txt')
            with open(filename, 'r') as file:
                file_contents = file.read()

            elements = file_contents.strip('()').split(', ')
            filename = elements[0].strip("'")
            filename = os.path.basename(filename)

            full_path = os.path.join(self.config.checkpoints_dir, filename)
            class_name = self.__class__.__name__
            function_name = ModelConfig._extract_load_from.__name__
            self.logger.call(class_name,
                             function_name,
                             additional_info="_extract_load_from: {0}".format(full_path))
            return full_path
        return self.load_from_link

    def _get_config(self):
        """
        Fetches the configuration from a file.

        Returns:
            Config: Configuration object.
        """
        return Config.fromfile(self.full_config_path)

    def _extract_classes(self) -> Tuple[Any, ...]:
        """
        Extracts classes based on the dataset type.

        Returns:
            Tuple: Tuple of extracted classes.
        """
        if self.config.dataset_type == "CocoDataset":
            with open(os.path.join(self.config.dataset_dir, self.config.train_json), 'r') as f:
                data = json.load(f)

            categories = data['categories']
            class_names = [category['name'] for category in categories]
            unique_class_names = tuple(set(class_names))
            class_name = self.__class__.__name__
            function_name = ModelConfig._extract_classes.__name__
            self.logger.call(class_name,
                             function_name,
                             additional_info="Classes in COCO dataset: {0}".format(str(unique_class_names)))
            return unique_class_names

    def set_custom_params(self):
        """
        Sets custom parameters for the model configuration.
        """
        cfg = self._get_config()
        PREFIX = self.config.dataset_dir if self.config.dataset_dir.endswith("/") else self.config.dataset_dir + "/"
        classes = self._extract_classes()
        cfg.dataset_type = self.config.dataset_type
        cfg.data_root = PREFIX
        cfg.metainfo = {
            'classes': classes,
            'palette': [
                (220, 20, 60),
            ]
        }

        cfg.train_dataloader.dataset.data_prefix = dict(img='train/')
        cfg.train_dataloader.dataset.metainfo = cfg.metainfo
        cfg.train_dataloader.dataset.ann_file = self.config.train_json
        cfg.train_dataloader.dataset.type = self.config.dataset_type
        cfg.train_dataloader.dataset.data_root = cfg.data_root

        cfg.val_dataloader.dataset.data_prefix = dict(img='test/')
        cfg.val_dataloader.dataset.metainfo = cfg.metainfo
        cfg.val_dataloader.dataset.ann_file = self.config.test_json
        cfg.val_dataloader.dataset.type = self.config.dataset_type
        cfg.val_dataloader.dataset.data_root = cfg.data_root

        cfg.test_dataloader.dataset.data_prefix = dict(img='test/')
        cfg.test_dataloader.dataset.metainfo = cfg.metainfo
        cfg.test_dataloader.dataset.ann_file = self.config.test_json
        cfg.test_dataloader.dataset.type = self.config.dataset_type
        cfg.test_dataloader.dataset.data_root = cfg.data_root

        cfg.test_evaluator.ann_file = cfg.data_root + self.config.test_json
        cfg.val_evaluator.ann_file = cfg.data_root + self.config.test_json

        cfg.default_hooks.checkpoint.save_best = 'auto'
        cfg.default_hooks.checkpoint.max_keep_ckpts = 5
        cfg.default_hooks.checkpoint.interval = 2

        try:
            cfg.model.test_cfg.rcnn.score_thr = 0.1
        except Exception as e:
            class_name = self.__class__.__name__
            function_name = ModelConfig.set_custom_params.__name__
            self.logger.call(class_name,
                             function_name,
                             additional_info="Error adding score_thr to test_cfg: {0}".format(e))

            cfg.model.test_cfg.score_thr = 0.1
        cfg.default_hooks.early_stopping = dict(
                type="EarlyStoppingHook",
                monitor="coco/bbox_mAP",
                patience=20,
                min_delta=0.01)

        if 'roi_head' in cfg.model:
            cfg.model.roi_head.bbox_head.num_classes = len(classes)
        else:
            cfg.model.bbox_head.num_classes = len(classes)

        cfg.train_dataloader.batch_size = 16

        max_epochs = self.config.epoch_number

        cfg.max_epochs = max_epochs
        cfg.train_cfg.max_epochs = max_epochs

        linear_epochs = max_epochs // 2

        if cfg.param_scheduler[1].type == "MultiStepLR":
            milestone_1 = max_epochs // 5 * 2
            milestone_2 = max_epochs // 5 * 4
            cfg.param_scheduler[0].end = linear_epochs
            cfg.param_scheduler[1].end = max_epochs
            cfg.param_scheduler[1].milestones = [milestone_1, milestone_2]
        elif cfg.param_scheduler[1].type == "CosineAnnealingLR":
            cfg.param_scheduler[0].end = linear_epochs
            cfg.param_scheduler[1].T_max = max_epochs
            cfg.param_scheduler[1].begin = linear_epochs
            cfg.param_scheduler[1].end = max_epochs

        # cfg.train_dataloader.dataset.pipeline.append(dict(type='RandAugment', aug_num=2),)

        cfg.load_from = self.load_from
        cfg.work_dir = self.config.models_dir
        custom_conf_path = os.path.splitext(os.path.basename(self.full_config_path))[0] + "_custom.py"

        print(f"Default Config:\n{cfg.pretty_text}")

        class_name = self.__class__.__name__
        function_name = ModelConfig.set_custom_params.__name__
        self.logger.call(class_name,
                         function_name,
                         additional_info="dump to {0}".format(os.path.join(self.config.conf_dir, custom_conf_path)))

        cfg.dump(os.path.join(self.config.conf_dir, custom_conf_path))


