import mmdet
from mmengine.utils import get_git_hash
from mmengine.utils.dl_utils import collect_env as collect_base_env


class EnvironmentCollector:
    """
    A class to collect and display environment information related to MMDetection and its dependencies.
    """

    def __init__(self):
        """
        Initializes the EnvironmentCollector instance.
        """
        self.env_info = self.collect_env()

    @staticmethod
    def collect_env():
        """
        Collects environment information.

        Returns:
            dict: A dictionary containing environment information.
        """
        env_info = collect_base_env()
        env_info['MMDetection'] = f'{mmdet.__version__}+{get_git_hash()[:7]}'
        return env_info

    def display_env_info(self):
        """
        Prints the collected environment information.
        """
        for name, val in self.env_info.items():
            print(f'{name}: {val}')
