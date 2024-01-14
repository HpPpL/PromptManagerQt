import os

# Путь к директории, где находятся файлы

directory_path = "../../images/unprocessed/temp"

# Получаем список файлов в директории
file_list = os.listdir(directory_path)

# Отфильтровываем PNG файлы и сортируем их лексикографически
png_files = sorted([file for file in file_list if file.lower().endswith('.png')])

# Генерируем новые имена файлов в нужном формате
new_file_names = [f"{i+1}-1.png" for i in range(len(png_files))]

# Переименовываем файлы
for old_name, new_name in zip(png_files, new_file_names):
    os.rename(os.path.join(directory_path, old_name), os.path.join(directory_path, new_name))

# Выводим сообщение об успешном выполнении
print("Файлы успешно переименованы")
