import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from auto_od.core.logger import Logger
from auto_od.core.settings import load_settings_from_yaml


class Analyzer:
    """
    A class for analyzing object detection datasets.

    Attributes:
        annotations (dict): Loaded annotations from the dataset.
        dataset_dir (str): Directory where the dataset is located.
        config (Settings): Configuration settings loaded from a YAML file.
        logger (Logger): Logger for logging information.
    """

    def __init__(self, settings_path: str, annotation_path: str, dataset_dir: str):
        """
        Initialize the Analyzer with dataset and configuration settings.

        Args:
            settings_path (str): Path to the YAML file containing settings.
            annotation_path (str): Path to the JSON file containing annotations.
            dataset_dir (str): Directory where the dataset is located.
        """
        self.annotations = self.load_annotations(annotation_path)
        self.dataset_dir = dataset_dir
        self.config = load_settings_from_yaml(settings_path)
        self.logger = Logger(self.config.base_dir)

    @staticmethod
    def load_annotations(annotation_path: str) -> dict:
        """
        Load annotations from a JSON file.

        Args:
            annotation_path (str): Path to the JSON file containing annotations.

        Returns:
            dict: Loaded annotations.
        """
        with open(annotation_path) as f:
            data = json.load(f)
        return data

    def analyze_object_sizes(self) -> list:
        """
        Analyze object sizes in the dataset.

        Returns:
            list: List of object sizes in the dataset.
        """
        sizes = []
        for ann in self.annotations['annotations']:
            bbox = ann['bbox']
            area = bbox[2] * bbox[3]
            sizes.append(area)
        return sizes

    def analyze_aspect_ratios(self) -> list:
        """
        Analyze aspect ratios of objects in the dataset.

        Returns:
            list: List of aspect ratios of objects.
        """
        ratios = []
        for ann in self.annotations['annotations']:
            bbox = ann['bbox']
            ratio = bbox[2] / bbox[3]
            ratios.append(ratio)
        return ratios

    def analyze_class_distribution(self) -> Counter:
        """
        Analyze class distribution in the dataset.

        Returns:
            Counter: Counts of objects per class.
        """
        classes = [ann['category_id'] for ann in self.annotations['annotations']]
        return Counter(classes)

    def plot_distribution(self, data: list, title: str, xlabel: str, ylabel: str, id: int):
        """
        Plot distribution of a given dataset attribute.

        Args:
            data (list): Data to plot.
            title (str): Title of the plot.
            xlabel (str): Label for the X-axis.
            ylabel (str): Label for the Y-axis.
            id (int): Identifier for the plot.
        """
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=50)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        class_name = self.__class__.__name__
        function_name = Analyzer.plot_distribution.__name__
        self.logger.call(class_name=class_name,
                         function_name=function_name,
                         additional_info=f"Plots are located in {self.dataset_dir}")
        plt.savefig(os.path.join(self.dataset_dir, f'plot_distribution{id}.jpg'))

    def suggest_config(self, img_dim: int, feature_map_scales: list) -> tuple:
        """
        Suggest anchor configurations based on dataset analysis.

        Args:
            img_dim (int): Dimension of the input image.
            feature_map_scales (list): Scales of feature maps.

        Returns:
            tuple: Suggested anchor configurations and class weighting.
        """
        sizes = self.analyze_object_sizes()
        ratios = self.analyze_aspect_ratios()
        class_dist = self.analyze_class_distribution()

        anchor_config = {}
        for scale in feature_map_scales:
            normalized_sizes = np.sqrt(sizes) / (img_dim / scale)
            anchor_sizes = [round(float(np.quantile(normalized_sizes, q)), 2) for q in [0.25, 0.5, 0.75]]
            aspect_ratios = [round(float(np.quantile(ratios, q)), 2) for q in [0.25, 1.0, 0.75]]
            anchor_config[scale] = {'anchor_sizes': anchor_sizes, 'aspect_ratios': aspect_ratios}

        class_weighting = 'recommended' if max(class_dist.values()) / min(class_dist.values()) > 2 else 'not required'
        class_name = self.__class__.__name__
        function_name = Analyzer.suggest_config.__name__
        self.logger.call(class_name=class_name,
                         function_name=function_name,
                         additional_info=f"Class Weighting is {class_weighting}")
        return anchor_config, class_weighting



# # cfg.model.bbox_head.anchor_generator.scales = [[round(s, 2) for s in config_suggestions['anchor_sizes']]]
# # cfg.model.bbox_head.anchor_generator.ratios = config_suggestions['aspect_ratios']
