class DatasetConverter:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        self.annotation_set = None

    def convert(self, **kwargs):
        raise NotImplementedError("Convert method must be implemented in the child class")
