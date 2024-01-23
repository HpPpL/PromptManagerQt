import json
import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


class ImageAnnotationViewer:
    """
    A class to view images and their corresponding annotations.

    Attributes:
        image_folder (str): The folder containing the images.
        json_file (str): The JSON file containing the annotations.
        annotations (dict): The loaded annotations from the JSON file.
        image_id_map (dict): A mapping from image filenames to their IDs.
        images (list): Sorted list of image filenames.
        current_image_index (int): Index of the currently displayed image.
        fig (matplotlib.figure.Figure): Matplotlib figure object.
        ax (matplotlib.axes.Axes): Matplotlib axes object.
        button_ax_prev (matplotlib.axes.Axes): Matplotlib axes object for the 'Previous' button.
        button_ax_next (matplotlib.axes.Axes): Matplotlib axes object for the 'Next' button.
        btn_prev (matplotlib.widgets.Button): 'Previous' button.
        btn_next (matplotlib.widgets.Button): 'Next' button.
    """

    def __init__(self, image_folder, json_file):
        """
        Initializes the ImageAnnotationViewer with the specified image folder and JSON file.

        Args:
            image_folder (str): The folder containing the images.
            json_file (str): The JSON file containing the annotations.
        """
        self.json_file = json_file
        self.image_folder = image_folder
        self.annotations = self.load_annotations()
        self.image_id_map = {img['file_name']: img['id'] for img in self.annotations['images']}
        self.images = sorted(os.listdir(image_folder))
        self.current_image_index = 0

        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)

        self.button_ax_prev = plt.axes([0.1, 0.05, 0.1, 0.075])
        self.button_ax_next = plt.axes([0.8, 0.05, 0.1, 0.075])
        self.btn_prev = Button(self.button_ax_prev, 'Previous')
        self.btn_next = Button(self.button_ax_next, 'Next')
        self.btn_prev.on_clicked(self.prev_image)
        self.btn_next.on_clicked(self.next_image)

        self.update_image()
        plt.show()

    def load_annotations(self):
        """! Loads annotations from the JSON file."""
        with open(self.json_file, 'r') as file:
            data = json.load(file)
        return data

    def show_image(self, img_path, img_annotations):
        """
        ! Displays an image and its annotations.

        @param img_path (str): The path to the image file.
        @param img_annotations (list): A list of annotations for the image.
        """
        self.ax.clear()
        img = plt.imread(img_path)
        self.ax.imshow(img)

        for ann in img_annotations:
            bbox = ann['bbox']
            rect = patches.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3], linewidth=2, edgecolor='r', facecolor='none')
            self.ax.add_patch(rect)

        plt.draw()

    def next_image(self, event):
        """Displays the next image."""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_image()

    def prev_image(self, event):
        """Displays the previous image."""
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.update_image()

    def update_image(self):
        """Updates the display with the current image and its annotations."""
        img_file = self.images[self.current_image_index]
        img_path = os.path.join(self.image_folder, img_file)
        img_id = self.image_id_map.get(img_file)
        img_annotations = [ann for ann in self.annotations['annotations'] if ann['image_id'] == img_id]
        self.show_image(img_path, img_annotations)


