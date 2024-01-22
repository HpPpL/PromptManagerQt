import os
import json

def process_directory(path):
    data = {
        "type": "section",
        "name": os.path.basename(path),
        "params": []
    }

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            data["params"].append(process_directory(item_path))
        elif item.lower().endswith(".webp"):
            image_name = os.path.splitext(item)[0]  # Имя файла без расширения
            image_data = {
                "type": "parametr",
                "name": image_name,
                "imgPath": item_path,
                "prompt": image_name.replace('_', ' '),
                'hint': "At the moment there is no hint to the selected parameter!"
            }
            data["params"].append(image_data)

    return data

root_directory = "All-Images/DreamStudio"
output_file = "DreamStudio.json"

if os.path.exists(root_directory):
    data = process_directory(root_directory)

    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Данные сохранены в {output_file}")
else:
    print(f"Указанная директория не существует: {root_directory}")
