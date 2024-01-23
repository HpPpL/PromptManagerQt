from __future__ import annotations

import os
import shutil

import requests
from tqdm import tqdm

from auto_od.core.logger import Logger


def extract_weights_and_config(model_info: dict) -> tuple | None:
    """
    Extracts weights and config file paths from the model information.

    Args:
        model_info (dict): A dictionary containing model information.

    Returns:
        tuple: A tuple containing a list of weights and config paths, and the task type.
    """
    try:
        return [model_info['Weights'], model_info['Config']], model_info['Results'][0]['Task']
    except KeyError:
        try:
            metrics = model_info['Results'][0]['Metrics']
            if 'Weights' in metrics:
                return [metrics['Weights'], metrics['Config']], model_info['Results'][0]['Task']
        except KeyError as e:
            pass
    return None


def get_config(source_file: str, mmdetection_dir: str, config_dir: str):
    """
    Copies a configuration file from the MMDetection directory to the specified config directory.

    Args:
        source_file (str): The source file name.
        mmdetection_dir (str): The directory of MMDetection.
        config_dir (str): The destination directory to copy the config file.
    """
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    shutil.copy(os.path.join(mmdetection_dir, source_file), config_dir)


def get_weights(base_dir: str, url: str, file_save_name: str, checkpoints_dir: str):
    """
    Downloads the weights from a URL and saves them in the specified directory.

    Args:
        base_dir (str): The base directory for logging.
        url (str): The URL to download the weights from.
        file_save_name (str): The name of the file to save the downloaded weights.
        checkpoints_dir (str): The directory to save the downloaded weights.
    """
    logger = Logger(base_dir)
    if not os.path.exists(checkpoints_dir):
        os.makedirs(checkpoints_dir)

    if not os.path.exists(os.path.join(checkpoints_dir, file_save_name)):
        logger.call(class_name="",
                    function_name="get_weights",
                    additional_info=f"Downloading {file_save_name}, url {url}")
        file = requests.get(url, stream=True)
        total_size = int(file.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(os.path.join(checkpoints_dir, file_save_name), 'wb') as f:
            for data in file.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
    else:
        logger.call(class_name="",
                    function_name="get_weights",
                    additional_info=f"File already present {file_save_name}")


def runs_archive(runs_archive_dir: str):
    """
    Creates a runs archive directory if it does not exist.

    Args:
        runs_archive_dir (str): The directory path for the runs archive.
    """
    if not os.path.exists(runs_archive_dir):
        os.makedirs(runs_archive_dir)
