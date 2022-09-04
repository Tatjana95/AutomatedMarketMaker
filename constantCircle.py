from marketMaker import MarketMaker
from swap import Swap
from token_class import Token
import math
from abc import abstractmethod

class ConstantCircle(MarketMaker):
    def __init__(self, token : [Token], a, b = 0):
        super().__init__(token)
        self.__a = a
        self.__b = b
                
    def cost_function(self):
        tokens = super().getTokens()
        s1 = 0
        s2 = 0
        for t in tokens:
            s1 += (t.getAmount() - self.__a)**2
        if self.__b != 0:
            for ti in tokens:
                for tj in tokens:
                    if ti != tj:
                        s2 += ti.getAmount()*tj.getAmount()
        return s1 + self.__b*s2
    
    def price_function(self, token):
        tokens = super().getTokens()
        s = 0
        if self.__b != 0:
            for t in tokens:
                if t != token:
                    s += t.getAmount()
        return 2*(token.getAmount() - self.__a) + self.__b*s
    def getA(self):
        return self.__a
    def getB(self):
        return self.__b    

class ConstantCircle_swap(ConstantCircle,Swap):
    def __init__(self, token : [Token], a, b):
        ConstantCircle.__init__(self, token, a, b)
        k = self.cost_function()
        Swap.__init__(self, k)
        
    def token1RelativePrice(self):
        tokens = ConstantCircle.getTokens(self)
        return ConstantCircle.price_function(self, tokens[0]) / ConstantCircle.price_function(self, tokens[1])
    def token2RelativePrice(self):
        tokens = ConstantCircle.getTokens(self)
        return ConstantCircle.price_function(self, tokens[1]) / ConstantCircle.price_function(self, tokens[0])
        
    def unknownAmount(self, n, token):
        try:
            amount1 =  -math.sqrt(Swap.getK(self) - (n-ConstantCircle.getA(self))**2) + ConstantCircle.getA(self)
        except:
            amount1 = 0
        try:
            amount2 = math.sqrt(Swap.getK(self) - (n-ConstantCircle.getA(self))**2) + ConstantCircle.getA(self)
        except:
            amount2 = 0
        if abs(amount1 - token.getAmount()) < abs(amount2  - token.getAmount()):
            return amount1
        else:
            return amount2
        
    def valueAsset0(self, token):
        initial = ConstantCircle.getInitialState(self)
        for i in initial:
            if i.getName() == token.getName():
                return 2 * i.getAmount()
    def valueAssetN(self, token):
        return 2 * token.getAmount()
    def valueAssetRelative(self, token):
        tokens = ConstantCircle.getTokens(self)
        initial = ConstantCircle.getInitialState(self)
        if token == tokens[0]:
            yn = tokens[0].getAmount()
            xn = tokens[1].getAmount()
        elif token == tokens[1]:
            yn = tokens[1].getAmount()
            xn = tokens[0].getAmount()
        if token.getName() == initial[0].getName():
            y0 = initial[0].getAmount()
            x0 = initial[1].getAmount()
        elif token.getName() == initial[1].getName():
            y0 = initial[1].getAmount()
            x0 = initial[0].getAmount()
        
        return (yn / xn) * x0 + y0 
        
    def impermanentLostAndGain(self, token):
        return self.valueAssetN(token) - self.valueAssetRelative(token)
                  
    def swap(self, action, token_name, quantity):
        tokens = ConstantCircle.getTokens(self)
        tradeToken = ConstantCircle.getTokenByName(self, token_name)
        if tradeToken == tokens[0]:
            depositeToken = tokens[1]
        elif tradeToken == tokens[1]:
            depositeToken = tokens[0]
            
        if action == 'buy':
            newStateOfTradeToken = tradeToken.getAmount() - quantity
        elif action == 'sell':
            newStateOfTradeToken = tradeToken.getAmount() + quantity
        
        newStateOfDepositeToken = self.unknownAmount(newStateOfTradeToken, depositeToken)
        pay = newStateOfDepositeToken - depositeToken.getAmount()
        tradeToken.setAmount(newStateOfTradeToken)
        depositeToken.setAmount(newStateOfDepositeToken)
        
        return pay
