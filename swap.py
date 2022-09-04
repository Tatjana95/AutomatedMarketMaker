from abc import abstractmethod
from marketMaker import MarketMaker
from token_class import Token

class Swap():
    def __init__(self, k):
        self._k = k
    def getK(self):
        return self._k
    def setK(self, k):
        self._k = k
    @abstractmethod
    def token1RelativePrice(self):
        pass
    @abstractmethod
    def token2RelativePrice(self):
        pass
    @abstractmethod
    def valueAsset0(self):
        pass
    @abstractmethod
    def valueAssetN(self):
        pass
    @abstractmethod
    def valueAssetRelative(self):
        pass
    @abstractmethod
    def impermanentLostAndGain(self):
        pass
    @abstractmethod
    def swap(self):
        pass