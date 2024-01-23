
class BaseSplit:
    def __init__(self, test_proportion=0.2):
        self.test_proportion = test_proportion

    def split_dataset(self, **kwargs):
        raise NotImplementedError("Subclasses must implement the split_dataset method.")
