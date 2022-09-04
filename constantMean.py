#!/usr/bin/env python
# coding: utf-8

# In[5]:


from marketMaker import MarketMaker
from swap import Swap
from token_class import Token
import math
from abc import abstractmethod


# In[6]:


class ConstantMean(MarketMaker):
    def __init__(self, token : [Token]):
        super().__init__(token)
                
    def cost_function(self):
        tokens = super().getTokens()
        p = 1
        for t in tokens:
            p *= t.getAmount()**t.getWeight()
        return p
    
    def price_function(self, token):
        tokens = super().getTokens()
        p = 1
        for t in tokens:
            if t != token:
                p *= t.getAmount()
        return token.getWeight()*token.getAmount()**(token.getWeight()-1)*p
    


# In[7]:


class ConstantMean_swap(ConstantMean,Swap):
    def __init__(self, token : [Token]):
        ConstantMean.__init__(self, token)
        k = self.cost_function()
        Swap.__init__(self, k)
        
    def token1RelativePrice(self):
        tokens = ConstantMean.getTokens(self)
        return ConstantMean.price_function(self, tokens[0]) / ConstantMean.price_function(self, tokens[1])
    def token2RelativePrice(self):
        tokens = ConstantMean.getTokens(self)
        return ConstantMean.price_function(self, tokens[1]) / ConstantMean.price_function(self, tokens[0])
        
    def unknownAmount(self, n, token):
        tokens = ConstantMean.getTokens(self)
        if tokens[0] == token:
            q = tokens[1].getWeight()
        elif tokens[1] == token:
            q = tokens[0].getWeight()
        return (Swap.getK(self) / (n**q))**(1/token.getWeight())
    
    def valueAsset0(self, token):
        initial = ConstantMean.getInitialState(self)
        for i in initial:
            if i.getName() == token.getName():
                return 2 * i.getAmount()
    def valueAssetN(self, token):
        return 2 * token.getAmount()
    def valueAssetRelative(self, token):
        tokens = ConstantMean.getTokens(self)
        initial = ConstantMean.getInitialState(self)
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
        tokens = ConstantMean.getTokens(self)
        tradeToken = ConstantMean.getTokenByName(self, token_name)
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

