import xml.etree.ElementTree as ET
import os

def modify_xml_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Удаление элементов <polygon>
            for obj in root.findall('.//object'):
                for polygon in obj.findall('polygon'):
                    obj.remove(polygon)

            # Изменение содержимого в <object> для 'person' и корректировка порядка элементов
            for obj in root.findall('.//object'):
                name = obj.find('name')
                if name is not None and name.text.lower() == 'person':
                    name.text = 'Person'
                    pose = ET.Element('pose')
                    truncated = ET.Element('truncated')
                    difficult = ET.Element('difficult')
                    pose.text = 'Unspecified'
                    truncated.text = '0'
                    difficult.text = '0'

                    bndbox = obj.find('bndbox')
                    obj.insert(1, pose)
                    obj.insert(2, truncated)
                    obj.insert(3, difficult)
                    obj.remove(bndbox)
                    obj.append(bndbox)

            # Удаление элементов <segmented>
            for segmented in root.findall('segmented'):
                root.remove(segmented)

            # Изменение <folder> и добавление <path>
            folder = root.find('folder')
            filename_element = root.find('filename')
            if folder is not None and filename_element is not None:
                folder.text = 'my-project-name'
                new_path = os.path.join('/my-project-name', filename_element.text)
                path_element = ET.Element('path')
                path_element.text = new_path
                root.insert(2, path_element)  # Вставка элемента <path> после <filename>

            # Изменение <database>
            for database in root.findall('.//database'):
                if database.text == 'roboflow.ai':
                    database.text = 'Unspecified'

            # Сохранение изменений в файл
            tree.write(file_path)

# Пример использования:
modify_xml_files('testdata')
