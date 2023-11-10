import os
import shutil

# Путь к начальной папке
initial_folder = "C:\\Users\\ender\\Desktop\\Test\\Add Some Details"

# Путь к папке, содержащей файлы для замены
replacement_folder = "C:\\Users\\ender\\Desktop\\Test\\Midjourney prompt generator - promptoMANIA_files"

# Получим список файлов в папке с заменой
replacement_files = os.listdir(replacement_folder)

cnt = 0

# Пройдемся по всем папкам и файлам в начальной папке
for root, dirs, files in os.walk(initial_folder):
    for filename in files:
        if filename in replacement_files:
            replacement_file_path = os.path.join(replacement_folder, filename)
            initial_file_path = os.path.join(root, filename)
            shutil.copy2(replacement_file_path, initial_file_path)
            # print(f'Заменен файл: {initial_file_path}')
            cnt += 1
print(f'Замена файлов завершена. Заменено файлов {cnt}')
