import os

from auto_od.core.logger import Logger


def find_last_train(base_directory: str) -> str:
    """
    Finds the most recently created training folder in a given base directory.

    Args:
        base_directory (str): The base directory where training folders are located.

    Returns:
        str: Path of the last (most recent) training folder. If no training folder exists,
             it returns the path of a new folder to be created.
    """
    counter = 1
    while True:
        folder_name = f"train{counter}"
        folder_path = os.path.join(base_directory, folder_name)

        if not os.path.exists(folder_path):
            if counter == 1:
                return str(os.path.join(base_directory, folder_name))
            else:
                return str(os.path.join(base_directory, f"train{counter - 1}"))
        counter += 1


def generate_train_folder(base_dir: str, run_archive_dir: str) -> str:
    """
    Generates a new training folder within the runs archive directory.

    Args:
        base_dir (str): The base directory of the project.
        run_archive_dir (str): The directory where training runs are archived.

    Returns:
        str: The path of the newly created training folder.
    """
    logger = Logger(base_dir)
    counter = 1
    while True:
        folder_name = f"train{counter}"
        folder_path = os.path.join(run_archive_dir, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.call(class_name="generate_train_folder",
                        function_name="generate_train_folder",
                        additional_info=f"Created {folder_name} folder.")
            return folder_path

        counter += 1
