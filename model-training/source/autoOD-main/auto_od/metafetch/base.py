import abc


class MetaFile:
    def __init__(self):
        pass

    @abc.abstractmethod
    def extractor(self, **kwargs):
        pass

    @abc.abstractmethod
    def parser(self, **kwargs):
        pass

    @abc.abstractmethod
    def download(self, **kwargs):
        pass
