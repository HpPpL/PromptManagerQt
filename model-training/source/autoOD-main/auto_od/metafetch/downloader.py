import glob as glob
import os
from typing import Any, List

import yaml

from auto_od.core.settings import load_settings_from_yaml
from auto_od.helper import metafile
from auto_od.helper.settings import generate_train_folder
from auto_od.metafetch.base import MetaFile


class MetaFileDownloader(MetaFile):
    """
    MetaFileDownloader is responsible for downloading metafiles
    (which include model weights and configuration files) based on the specified settings.

    Attributes:
        settings_path (str): Path to the settings YAML file.
    """
    def __init__(self, settings_path: str):
        """
        Initialize the MetaFileDownloader object.

        Args:
            settings_path (str): Path to the settings YAML file.
        """
        self.settings_path = settings_path
        super().__init__()

    def extractor(self, yaml_file: Any, weights_and_config: list) -> List[str]:
        """
        Extracts weight and configuration file information from a given YAML file.

        Args:
            yaml_file (Any): Loaded YAML file containing model metadata.
            weights_and_config (list): List to accumulate the extracted weight and config paths.

        Returns:
            List[str]: Updated list with extracted weight and configuration file paths.
        """
        config = load_settings_from_yaml(self.settings_path)

        if 'Models' in yaml_file:
            for model_info in yaml_file['Models']:
                result = metafile.extract_weights_and_config(model_info=model_info)
                if result and result[1] == config.task:
                    weights_and_config.append(result[0])
        else:
            for model_info in yaml_file:
                result = metafile.extract_weights_and_config(model_info=model_info)
                if result and result[1] == config.task:
                    weights_and_config.append(result[0])

        return weights_and_config

    def parser(self) -> List[str]:
        """
        Parses all metafiles and extracts weights and configuration file information.

        Returns:
            List[str]: List containing tuples of weights URL and configuration file path.
        """
        config = load_settings_from_yaml(self.settings_path)
        root_meta_file_path = config.mmdet_config
        all_meta_file_paths = glob.glob(os.path.join(root_meta_file_path, '*', 'metafile.yml'), recursive=True)
        weights_conf_list = []

        for meta_file_path in all_meta_file_paths:
            with open(meta_file_path, 'r') as f:
                yaml_file = yaml.safe_load(f)
            weights_conf_list = self.extractor(yaml_file, weights_conf_list)

        return weights_conf_list

    def download(self, model_name: str):
        """
        Downloads the model weights and configuration file for the specified model.

        Args:
            model_name (str): Name of the model for which weights and config are to be downloaded.
        """
        config = load_settings_from_yaml(self.settings_path)

        weights_list = self.parser()
        download_url, download_conf_file = None, None
        for weights in weights_list:
            print(f"Founds weights: {weights}")
            if model_name == weights[0].split('/')[-2]:
                download_url = weights[0]
                download_conf_file = weights[1]
                break

        assert download_url is not None, f"{model_name} weight file not found!!!"
        assert download_conf_file is not None, f"{model_name} config file not found!!!"

        self.save_paths(download_url, download_conf_file, model_name)
        metafile.get_weights(base_dir=config.base_dir, url=download_url, file_save_name=download_url.split('/')[-1], checkpoints_dir=config.checkpoints_dir)
        metafile.get_config(source_file=download_conf_file, mmdetection_dir=config.mmdet_dir, config_dir=config.conf_dir)

    def write_weights_txt_file(self):
        """
        Writes a text file containing all available weights and configurations.
        """
        config = load_settings_from_yaml(self.settings_path)
        weights_list = self.parser()

        with open(os.path.join(config.train_dir, 'weights.txt'), 'w') as f:
            for weights in weights_list:
                f.writelines(f"{weights}\n")

    def save_paths(self, download_url: str, download_conf_file: str, model_name: str):
        """
        Saves the download paths for weights and config files to a text file.

        Args:
            download_url (str): URL of the model weights.
            download_conf_file (str): Path of the model configuration file.
            model_name (str): Name of the model.
        """
        config = load_settings_from_yaml(self.settings_path)

        with open(os.path.join(config.train_dir, 'paths.txt'), 'w') as f:
            f.writelines(f"{download_url, download_conf_file, model_name}\n")

    def __call__(self, model_name: str = "rtmdet_s_8xb32-300e_coco"):
        """
        Callable method for downloading a specific model's weights and config files.

        Args:
            model_name (str, optional): Name of the model to download. Defaults to "rtmdet_s_8xb32-300e_coco".
        """
        config = load_settings_from_yaml(self.settings_path)

        metafile.runs_archive(config.runs_archive_dir)  # create folder runs_archive
        generate_train_folder(config.base_dir, config.runs_archive_dir)  # create train folder in runs_archive folder

        self.write_weights_txt_file()  # Write a text file with all available weights
        self.download(model_name)
