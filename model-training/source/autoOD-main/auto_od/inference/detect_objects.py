from pathlib import Path

import torch
from mmdet.apis import DetInferencer


class Inference:
    """
    A class for performing inference using a detection model from the mmdetection library.

    This class initializes with the model's configuration file and checkpoint file,
    and provides methods to perform detection on image frames.

    Attributes:
        config_file (str): Path to the model's configuration file.
        checkpoint_file (str): Path to the model's checkpoint file.
    """

    def __init__(self, config_file: str, checkpoint_file: str, device: str = "cpu"):
        """
        Initializes the Inference class with specified model configuration and checkpoint files.

        Args:
            config_file (str): Path to the model's configuration file.
            checkpoint_file (str): Path to the model's checkpoint file.
        """

        if device is not None and "cuda" in device and not torch.cuda.is_available():
            raise Exception("Selected device='{0}', but cuda is not available to Pytorch.".format(device))
        elif device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.device = device
        self.config_file = config_file
        self.checkpoint_file = checkpoint_file

        self.inferencer = self.detect_frame()

    def detect_frame(self):
        """
        Initializes the model for inference.

        Returns:
            DetInferencer: An instance of the DetInferencer for running detection.
        """
        assert Path(self.checkpoint_file).is_file(), TypeError(f"{self.checkpoint_file} should be a checkpoint file.")
        assert Path(self.config_file).is_file(), TypeError(f"{self.config_file} should be a config file.")
        return DetInferencer(self.config_file, self.checkpoint_file, self.device)

    def process(self, frame: any, return_vis: bool = False, out_dir: str = '') -> dict:
        """
        Performs detection on a given image frame and saves the result.

        Args:
            frame (any): Path to the image frame to be processed.
            return_vis (bool): Is return in output visualisation array.
            out_dir (str, optional): Directory where the output should be saved. Defaults to ''.

        Returns:
            dict: The result of detection, typically including detected objects' bounding boxes, labels, and scores.
        """
        result = self.inferencer(frame, return_vis=return_vis, out_dir=out_dir)
        return result


