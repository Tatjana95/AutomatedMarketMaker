from marketMaker import MarketMaker
from swap import Swap
from token_class import Token
import math
from abc import abstractmethod

class LS_LMSR(MarketMaker):
    def __init__(self, token : [Token], alpha):
        super().__init__(token)
        self.__alpha = alpha
                
    def b_function(self):
        tokens = super().getTokens()
        s = 0
        for t in tokens:
            s += t.getAmount()
        return self.__alpha*s
            
    def cost_function(self):
        tokens = super().getTokens()
        b = self.b_function()
        q1 = tokens[0].getAmount()
        s = 0
        for t in tokens:
            s += math.e**((t.getAmount() - q1) / b)
        return q1 + b*math.log(s)
    
    def price_function(self, token):
        #q_i = token.getAmount()
        tokens = super().getTokens()
        b = self.b_function()
        sE = 0
        sQ = 0
        sQE = 0
        for t in tokens:
            sE += math.e**(t.getAmount()/b)
            sQ += t.getAmount()
            sQE += t.getAmount()*(math.e**(t.getAmount()/b))
        return self.__alpha*math.log(sE) + ((math.e**(token.getAmount()/b))*sQ - sQE)/(sQ*sE)
    
    def getAlpha(self):
        return self.__alpha

class LS_LMSR_swap(LS_LMSR,Swap):
    def __init__(self, token : [Token], alpha):
        LS_LMSR.__init__(self, token, alpha)
        k = self.cost_function()
        Swap.__init__(self, k)
        
    def token1RelativePrice(self):
        tokens = LS_LMSR.getTokens(self)
        return LS_LMSR.price_function(self, tokens[0]) / LS_LMSR.price_function(self, tokens[1])
    def token2RelativePrice(self):
        tokens = LS_LMSR.getTokens(self)
        return LS_LMSR.price_function(self, tokens[1]) / LS_LMSR.price_function(self, tokens[0])
        
    def unknownAmount(self, n):
        #b = LS_LMSR.b_function(self)
        #print(b)
        eps = 0.000000001
        start = eps
        init = LS_LMSR.getInitialState(self)
        end = init[0].getAmount() + init[1].getAmount()
        while 1:
            b_start = LS_LMSR.getAlpha(self)*(n + start)
            f_start = Swap.getK(self) + b_start*math.log(1 - math.e**((n-Swap.getK(self)) / b_start)) -start
            y = (start + end) / 2
            b = LS_LMSR.getAlpha(self)*(n + y)
            f_y = Swap.getK(self) + b*math.log(1 - math.e**((n-Swap.getK(self)) / b)) -y
           # print('start: ', start, ' end: ', end, 'f_start: ',f_start, 'y: ', y,' f_y: ', f_y)
            if abs(f_y) < eps:
                return y
            elif f_start*f_y < 0:
                end = y
            else:
                start = y
      
    def valueAsset0(self, token):
        initial = LMSR.getInitialState(self)
        for i in initial:
            if i.getName() == token.getName():
                return 2 * i.getAmount()
    def valueAssetN(self, token):
        return 2 * token.getAmount()
    def valueAssetRelative(self, token):
        tokens = LS_LMSR.getTokens(self)
        initial = LS_LMSR.getInitialState(self)
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
        #return self.valueAssetN(token) - self.valueAssetRelative(token)
        tokens = LS_LMSR.getTokens(self)
        initial = LS_LMSR.getInitialState(self)
        return (2 - (initial[0].getAmount() / tokens[0].getAmount()))*tokens[1].getAmount()- initial[1].getAmount()
    
    def swap(self, action, token_name, quantity):
        tokens = LS_LMSR.getTokens(self)
        tradeToken = LS_LMSR.getTokenByName(self, token_name)
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

class LS_LMSR_prediction(LS_LMSR):
    def __init__(self, token : [Token], alpha):
        super().__init__(token, alpha)

    def trade(self, token_name, quantity):
        tokens = LS_LMSR.getTokens(self)
        tradeToken = LS_LMSR.getTokenByName(self, token_name)
        
        cost1 = self.cost_function()
        
        newStateOfTradeToken = tradeToken.getAmount() + quantity
        
        tradeToken.setAmount(newStateOfTradeToken)
        pay = self.cost_function() - cost1
        return pay
