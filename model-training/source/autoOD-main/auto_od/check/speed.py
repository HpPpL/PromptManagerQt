# check model's speed

import os
import time
from pathlib import Path
import torch

from mmdet.apis import inference_detector, init_detector


class InferenceTimeAnalyzer:
    def __init__(self, config_file: str, checkpoint_file: str, image_folder: str, device: str = 'cpu'):
        """
        Initializes the InferenceTimeAnalyzer.

        Args:
            config_file (str): Path to the model configuration file.
            checkpoint_file (str): Path to the model checkpoint file.
            image_folder (str): Path to the folder containing images for inference.
            device (str): Device to run inference on. Defaults to 'cpu'.
        """
        if device is not None and "cuda" in device and not torch.cuda.is_available():
            raise Exception("Selected device='{0}', but cuda is not available to Pytorch.".format(device))
        elif device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"

        assert Path(checkpoint_file).is_file(), TypeError(f"{checkpoint_file} should be a checkpoint file.")
        assert Path(config_file).is_file(), TypeError(f"{config_file} should be a config file.")
        self.model = init_detector(config_file, checkpoint_file, device=device)
        self.image_folder = image_folder

    def get_average_inference_time(self) -> float:
        """
        Calculates the average inference time for images in the specified folder.

        Returns:
            float: Average inference time in milliseconds.
        """
        image_files = [os.path.join(self.image_folder, file) for file in os.listdir(self.image_folder)
                       if file.endswith(('.jpg', '.jpeg', '.png'))]

        total_time = 0
        for image_file in image_files:
            start_time = time.time()
            _ = inference_detector(self.model, image_file)
            end_time = time.time()
            total_time += (end_time - start_time)

        average_time = total_time / len(image_files)
        return average_time * 1000  # in milliseconds

