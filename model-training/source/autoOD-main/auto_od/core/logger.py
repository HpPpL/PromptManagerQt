import datetime
import logging
import os.path


class Logger:
    def __init__(self, base_dir: str):
        log_file = os.path.join(base_dir, "auto_od.log")
        self.logger = logging.getLogger('Logger')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def call(self, class_name, function_name, additional_info=None):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"Class '{class_name}' - Function '{function_name}' called at {timestamp}"
        if additional_info:
            log_message += f" - Additional Info: {additional_info}"
        self.logger.info(log_message)


