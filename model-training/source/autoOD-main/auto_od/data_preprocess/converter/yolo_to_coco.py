# in development


# import os
# import shutil
#
# from globox import AnnotationSet
#
# from auto_od.data_preprocess.converter.base import DatasetConverter
#
#
# class YOLOToCocoConverter:
#     def __init__(self, annotation_dir: str = "", images_dir: str = ""):
#         self.annotation_dir = annotation_dir
#         self.images_dir = images_dir
#         self.annotation_set = AnnotationSet.from_yolo(folder=self.annotation_dir,
#                                                       image_folder=self.images_dir).map_labels({"0": "weapon",})
#
#     def convert(self, save_path: str):
#         """
#         Convert the dataset from XML to COCO format and save it.
#
#         Args:
#             save_path (str): Path where the converted COCO format dataset should be saved.
#         """
#         # os.makedirs(self.new_dataset_dir, exist_ok=True)
#         print(self.annotation_set.show_stats())
#         self.annotation_set.save_pascal_voc(save_path)
#         # self.annotation_set.save_coco(save_path, auto_ids=True)
#
#         # for image_id in self.annotation_set.image_ids:
#         #     image_path = os.path.join(self.dataset_dir, image_id)
#         #     new_image_path = os.path.join(self.new_dataset_dir, image_id)
#         #     shutil.copy(image_path, new_image_path)
#
#     @staticmethod
#     def stats_info(json_file_train: str, json_file_test: str = ''):
#         """
#         Display statistics information about the dataset.
#
#         Args:
#             json_file_train (str): Path to the COCO format JSON file for the training set.
#             json_file_test (str, optional): Path to the COCO format JSON file for the test set. Defaults to ''.
#         """
#         annotation_set = AnnotationSet.from_coco(json_file_train)
#         print(annotation_set.show_stats())
#         if json_file_test:
#             annotation_set = AnnotationSet.from_coco(json_file_test)
#             print(annotation_set.show_stats())
#
# #
# # c = YOLOToCocoConverter(annotation_dir="/Users/elinachertova/Downloads/CCTV_Guns_Dataset/labels",
# #                         images_dir="/Users/elinachertova/Downloads/CCTV_Guns_Dataset/images")
#
# # c.convert(save_path="/Users/elinachertova/Downloads/CCTV_Guns_Dataset/xml_labels")
#
# c = YOLOToCocoConverter(annotation_dir="/Users/elinachertova/Downloads/CCTV_Guns_Dataset/labels",
#                         images_dir="/Users/elinachertova/Downloads/CCTV_Guns_Dataset/images")
#
# c.convert(save_path="/Users/elinachertova/Downloads/CCTV_Guns_Dataset/xml_labels")
#
