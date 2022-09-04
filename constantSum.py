#!/usr/bin/env python
# coding: utf-8

# In[1]:


from marketMaker import MarketMaker
from swap import Swap
from token_class import Token
import math
from abc import abstractmethod


# In[2]:


class ConstantSum(MarketMaker):
    def __init__(self, token : [Token]):
        super().__init__(token)
                
    def cost_function(self):
        tokens = super().getTokens()
        s = 0
        for t in tokens:
            s += t.getAmount()
        return s
    
    def price_function(self, token):
        return 1
    


# In[3]:


class ConstantSum_swap(ConstantSum,Swap):
    def __init__(self, token : [Token]):
        ConstantSum.__init__(self, token)
        k = self.cost_function()
        Swap.__init__(self, k)
        
    def token1RelativePrice(self):
        tokens = ConstantSum.getTokens(self)
        return ConstantSum.price_function(self, tokens[0]) / ConstantSum.price_function(self, tokens[1])
    def token2RelativePrice(self):
        tokens = ConstantSum.getTokens(self)
        return ConstantSum.price_function(self, tokens[1]) / ConstantSum.price_function(self, tokens[0])
        
    def unknownAmount(self, n):
        return Swap.getK(self) - n
    
    def valueAsset0(self, token):
        initial = ConstantSum.getInitialState(self)
        for i in initial:
            if i.getName() == token.getName():
                return 2 * i.getAmount()
    def valueAssetN(self, token):
        return 2 * token.getAmount()
    def valueAssetRelative(self, token):
        tokens = ConstantSum.getTokens(self)
        initial = ConstantSum.getInitialState(self)
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
        
        tokens = ConstantSum.getTokens(self)
        initial = ConstantSum.getInitialState(self)
        if token == tokens[0]:
            t = tokens[1]
            i = initial[1]
        else:
            t = tokens[0]
            i = initial[0]
        
        return (2 - i.getAmount()/t.getAmount())*(Swap.getK(self) - t.getAmount()) - (Swap.getK(self)-i.getAmount())
                  
    def swap(self, action, token_name, quantity):
        tokens = ConstantSum.getTokens(self)
        tradeToken = ConstantSum.getTokenByName(self, token_name)
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

