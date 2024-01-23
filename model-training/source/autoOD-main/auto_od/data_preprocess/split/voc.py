# in development

# import os
# import xml.etree.ElementTree as ET
#
# from auto_od.data_preprocess.split.base import BaseSplit
#
#
# class PascalVocSplit(BaseSplit):
#     def split_dataset(self):
#         xml_files = [f for f in os.listdir(os.path.join(self.dataset_dir, 'Annotations')) if f.endswith('.xml')]
#         class_counts = {}
#         test_counts = {}
#
#         train_output_dir, test_output_dir = self.create_output_dirs()
#
#         for xml_file in xml_files:
#             tree = ET.parse(os.path.join(self.dataset_dir, 'Annotations', xml_file))
#             root = tree.getroot()
#             has_test_class = False
#
#             for obj in root.findall('object'):
#                 class_name = obj.find('name').text
#
#                 if class_name not in class_counts:
#                     class_counts[class_name] = 0
#                     test_counts[class_name] = 0
#                 class_counts[class_name] += 1
#
#                 if test_counts[class_name] < class_counts[class_name] * self.test_proportion:
#                     test_output_file = os.path.join(test_output_dir, xml_file)
#                     has_test_class = True
#                     test_counts[class_name] += 1
#                     break
#
#             if not has_test_class:
#                 train_output_file = os.path.join(train_output_dir, xml_file)
#             else:
#                 test_output_file = os.path.join(test_output_dir, xml_file)
#
#             if has_test_class:
#                 ET.ElementTree(root).write(test_output_file)
#             else:
#                 ET.ElementTree(root).write(train_output_file)
#
#
# if __name__ == '__main__':
#     dataset_dir = 'path_to_dataset_directory'  # Replace with your dataset directory
#     output_dir = 'path_to_output_directory'      # Replace with your desired output directory
#
#     pascal_voc_splitter = PascalVocSplit(dataset_dir, os.path.join(output_dir, 'pascal_voc'))
#     # coco_splitter = CocoSplit(dataset_dir, os.path.join(output_dir, 'coco'))
#
#     pascal_voc_splitter.split_dataset()
#     # coco_splitter.split_dataset()