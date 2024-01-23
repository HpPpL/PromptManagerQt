import json
import os
import random
import shutil
from collections import defaultdict


class BalancedCOCOSplitter:
    """
    Class to split and balance COCO-style datasets.

    Parameters:
        coco_file (str): Path to the COCO annotation file.
        image_dir (str): Directory containing the images.
        seed (int): Seed for random operations.

    Methods:
        create_balanced_subset(oversample=False)
        split_dataset(balanced_data, train_ratio=0.8)
        save_split_data(dataset, subset, output_dir, output_file)
    """

    def __init__(self, coco_file: str, image_dir: str, seed: int = 42):
        """
        Initialize the splitter with necessary parameters.

        Args:
            coco_file (str): Path to the COCO annotation file.
            image_dir (str): Directory containing the images.
            seed (int): Seed for random operations.
        """
        self.coco_file = coco_file
        self.image_dir = image_dir
        self.seed = seed
        self.data = self._load_data()
        self.class_images = defaultdict(list)
        self._organize_data()

    def _load_data(self):
        with open(self.coco_file, 'r') as f:
            return json.load(f)

    def _organize_data(self):
        image_ids_with_annotations = set()
        for ann in self.data['annotations']:
            image_id = ann['image_id']
            category_id = ann['category_id']
            self.class_images[category_id].append(image_id)
            image_ids_with_annotations.add(image_id)

        for image in self.data['images']:
            if image['id'] not in image_ids_with_annotations:
                self.class_images[-1].append(image['id'])

    def create_balanced_subset(self, oversample: bool = False):
        """
        Create a balanced subset of the dataset.

        Args:
            oversample (bool): Whether to oversample classes with fewer samples.

        Returns:
            dict: Balanced subset of the COCO dataset.
        """
        max_samples_per_class = max([len(images) for images in self.class_images.values()])

        balanced_images = set()
        random.seed(self.seed)

        for class_id, images in self.class_images.items():
            if len(images) < max_samples_per_class and oversample:
                oversampled_images = images * (max_samples_per_class // len(images)) + images[
                                                                                       :max_samples_per_class % len(
                                                                                           images)]
                balanced_images.update(oversampled_images)
            else:
                balanced_images.update(images)

        balanced_annotations = [ann for ann in self.data['annotations'] if ann['image_id'] in balanced_images]
        balanced_images_info = [img for img in self.data['images'] if img['id'] in balanced_images]

        return {
            'images': balanced_images_info,
            'annotations': balanced_annotations,
            'categories': self.data['categories']
        }

    @staticmethod
    def split_dataset(balanced_data: dict, train_ratio=0.8):
        """
        Split the dataset into training and testing sets.

        Args:
            balanced_data (dict): Balanced subset of the COCO dataset.
            train_ratio (float): Ratio of images to include in the training set.

        Returns:
            tuple: Training and testing sets.
        """
        images = balanced_data['images']
        random.shuffle(images)
        n_total = len(images)
        n_train = int(n_total * train_ratio)

        train_set = images[:n_train]
        test_set = images[n_train:]

        return train_set, test_set

    def save_split_data(self, dataset, subset, output_dir, output_file):
        """
        Save the split data to specified directories and files.

        Args:
            dataset (dict): Original COCO dataset.
            subset (list): Subset of images to save.
            output_dir (str): Directory to save the images.
            output_file (str): File to save the annotations.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        subset_annotations = [ann for ann in dataset['annotations'] if ann['image_id'] in [img['id'] for img in subset]]
        subset_data = {
            'images': subset,
            'annotations': subset_annotations,
            'categories': dataset['categories']
        }

        with open(output_file, 'w') as f:
            json.dump(subset_data, f, indent=4)

        for img in subset:
            file_name = img['file_name']
            shutil.copy(os.path.join(self.image_dir, file_name), os.path.join(output_dir, file_name))

    def __call__(self, output_train_dir, output_train_json, output_test_dir, output_test_json):
        balanced_data = self.create_balanced_subset()
        train_set, test_set = self.split_dataset(balanced_data, train_ratio=0.8)

        self.save_split_data(balanced_data, train_set,
                             output_train_dir,
                             output_train_json)
        self.save_split_data(balanced_data,
                             test_set,
                             output_test_dir,
                             output_test_json)


def load_json(file_path: str):
    """
    Load JSON data from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Loaded JSON data.
    """
    with open(file_path, 'r') as file:
        return json.load(file)


def save_json(data: dict, file_path: str):
    """
    Save data to a JSON file.

    Args:
        data (dict): Data to be saved.
        file_path (str): Path to the JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def join_coco_annotations(file_path1: str, file_path2: str, output_file_path: str):
    """
    Joins two COCO annotation files into a single file.

    This function merges two COCO datasets by updating image, annotation,
    and category IDs to ensure they are unique across the combined dataset.

    Args:
        file_path1 (str): Path to the first COCO annotation file.
        file_path2 (str): Path to the second COCO annotation file.
        output_file_path (str): Path where the combined annotation file will be saved.

    Returns:
        None: The combined annotation file is saved to the specified path.
    """
    data1 = load_json(file_path1)
    data2 = load_json(file_path2)

    max_image_id = max([img['id'] for img in data1['images']], default=0)
    max_annotation_id = max([ann['id'] for ann in data1['annotations']], default=0)
    max_category_id = max([cat['id'] for cat in data1['categories']], default=0)

    category_name_to_id = {cat['name']: cat['id'] for cat in data1['categories']}

    category_id_mapping = {}
    for cat in data2['categories']:
        if cat['name'] not in category_name_to_id:
            max_category_id += 1
            category_id_mapping[cat['id']] = max_category_id
            cat['id'] = max_category_id
            category_name_to_id[cat['name']] = max_category_id
            data1['categories'].append(cat)
        else:
            category_id_mapping[cat['id']] = category_name_to_id[cat['name']]

    image_id_mapping = {}
    for image in data2['images']:
        old_id = image['id']
        max_image_id += 1
        image_id_mapping[old_id] = max_image_id
        image['id'] = max_image_id

    for annotation in data2['annotations']:
        annotation['image_id'] = image_id_mapping[annotation['image_id']]
        annotation['category_id'] = category_id_mapping[annotation['category_id']]
        max_annotation_id += 1
        annotation['id'] = max_annotation_id

    combined_data = {
        'images': data1['images'] + data2['images'],
        'annotations': data1['annotations'] + data2['annotations'],
        'categories': data1['categories']
    }

    save_json(combined_data, output_file_path)
