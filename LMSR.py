from marketMaker import MarketMaker
from swap import Swap
from token_class import Token
import math
from abc import abstractmethod


class LMSR(MarketMaker):
    def __init__(self, token : [Token], b):
        super().__init__(token)
        self.__b = b
                
    def cost_function(self):
        tokens = super().getTokens()
        q1 = tokens[0].getAmount()
        s = 0
        for t in tokens:
            s += math.e**((t.getAmount() - q1) / self.__b)
        return q1 + self.__b*math.log(s)
    
    def price_function(self, token):
        q_i = token.getAmount()
        s = 0
        for t in super().getTokens():
            s += math.e**((t.getAmount() - q_i)/ self.__b)
        return 1/s
    
    def getB(self):
        return self.__b


class LMSR_swap(LMSR,Swap):
    def __init__(self, token : [Token], b):
        LMSR.__init__(self, token, b)
        k = self.cost_function()
        Swap.__init__(self, k)
        
    def token1RelativePrice(self):
        tokens = LMSR.getTokens(self)
        return LMSR.price_function(self, tokens[0]) / LMSR.price_function(self, tokens[1])
    def token2RelativePrice(self):
        tokens = LMSR.getTokens(self)
        return LMSR.price_function(self, tokens[1]) / LMSR.price_function(self, tokens[0])
        
    def unknownAmount(self, n):
        return Swap.getK(self) + LMSR.getB(self) * math.log(1 - math.e**((n - Swap.getK(self)) / LMSR.getB(self)))
    
    def valueAsset0(self, token):
        initial = LMSR.getInitialState(self)
        for i in initial:
            if i.getName() == token.getName():
                return 2 * i.getAmount()
    def valueAssetN(self, token):
        return 2 * token.getAmount()
    def valueAssetRelative(self, token):
        tokens = LMSR.getTokens(self)
        initial = LMSR.getInitialState(self)
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
        tokens = LMSR.getTokens(self)
        tradeToken = LMSR.getTokenByName(self, token_name)
        if tradeToken == tokens[0]:
            depositeToken = tokens[1]
        elif tradeToken == tokens[1]:
            depositeToken = tokens[0]
            
        if action == 'buy':
            newStateOfTradeToken = tradeToken.getAmount() - quantity
        elif action == 'sell':
            newStateOfTradeToken = tradeToken.getAmount() + quantity
        
        newStateOfDepositeToken = self.unknownAmount(newStateOfTradeToken)
        pay = newStateOfDepositeToken - depositeToken.getAmount()
            
        tradeToken.setAmount(newStateOfTradeToken)
        depositeToken.setAmount(newStateOfDepositeToken)
        
        return pay


class LMSR_prediction(LMSR):
    def __init__(self, token : [Token], b):
        super().__init__(token, b)

    def trade(self, token_name, quantity):
        tokens = LMSR.getTokens(self)
        tradeToken = LMSR.getTokenByName(self, token_name)
        
        cost1 = self.cost_function()
        
        newStateOfTradeToken = tradeToken.getAmount() + quantity
        
        tradeToken.setAmount(newStateOfTradeToken)
        pay = self.cost_function() - cost1
        #print('Korisnik placa :', pay, '$')
        return pay
    def worst_case_loss(self):
        return LMSR.getB(self) * math.log(len(LMSR.getTokens(self)))
