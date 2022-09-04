from abc import abstractmethod
from token_class import Token
import copy

class MarketMaker:
    def __init__(self, token : [Token]):#, token2 : Token):
        self._tokens = token
        self.__initialState = copy.deepcopy(token)
        #self._token2 = token2
    def getTokens(self):
        return self._tokens
    def getInitialState(self):
        return self.__initialState
    def getTokenByName(self, name):
        for t in self._tokens:
            if t.getName() == name:
                return t
    def poolState(self):
        for t in self._tokens:
            print('Token:\n\tname: ', t.getName(), '\tamount: ', round(t.getAmount(), 8))
    @abstractmethod
    def cost_function(self):
        pass
    @abstractmethod
    def price_function(self):
        pass
   