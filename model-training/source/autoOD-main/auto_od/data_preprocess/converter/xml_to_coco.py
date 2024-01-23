import os
import shutil

from globox import AnnotationSet

from auto_od.data_preprocess.converter.base import DatasetConverter


class XMLToCocoConverter(DatasetConverter):
    """
    A class for converting datasets from XML (PASCAL VOC) format to COCO format.

    Attributes:
        dataset_dir (str): Directory where the original dataset in XML format is located.
        new_dataset_dir (str): Directory where the new dataset in COCO format will be saved.
        annotation_set (AnnotationSet): Object representing the set of annotations in the dataset.
    """

    def __init__(self, dataset_dir: str = "", new_dataset_dir: str = ""):
        """
        Initialize the XMLToCocoConverter with dataset directories.

        Args:
            dataset_dir (str): Directory where the original dataset in XML format is located.
            new_dataset_dir (str): Directory where the new dataset in COCO format will be saved.
        """
        super().__init__(dataset_dir)
        self.new_dataset_dir = new_dataset_dir
        self.annotation_set = AnnotationSet.from_pascal_voc(self.dataset_dir)

    def convert(self, save_path: str):
        """
        Convert the dataset from XML to COCO format and save it.

        Args:
            save_path (str): Path where the converted COCO format dataset should be saved.
        """
        os.makedirs(self.new_dataset_dir, exist_ok=True)
        print(self.annotation_set.show_stats())
        self.annotation_set.save_coco(save_path, auto_ids=True)

        for image_id in self.annotation_set.image_ids:
            image_path = os.path.join(self.dataset_dir, image_id)
            new_image_path = os.path.join(self.new_dataset_dir, image_id)
            shutil.copy(image_path, new_image_path)

    @staticmethod
    def stats_info(json_file_train: str, json_file_test: str = ''):
        """
        Display statistics information about the dataset.

        Args:
            json_file_train (str): Path to the COCO format JSON file for the training set.
            json_file_test (str, optional): Path to the COCO format JSON file for the test set. Defaults to ''.
        """
        annotation_set = AnnotationSet.from_coco(json_file_train)
        print(annotation_set.show_stats())
        if json_file_test:
            annotation_set = AnnotationSet.from_coco(json_file_test)
            print(annotation_set.show_stats())

