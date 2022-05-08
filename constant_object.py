from abc import ABC


class ConstantObject(ABC):
    def process(self):
        pass

    def prepared(self):
        return True

    def destroyed(self):
        return False
