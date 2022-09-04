#!/usr/bin/env python
# coding: utf-8

# In[2]:


from marketMaker import MarketMaker
from swap import Swap
from token_class import Token
import math
from abc import abstractmethod


# In[3]:


class ConstantProduct(MarketMaker):
    def __init__(self, token : [Token]):
        super().__init__(token)
                
    def cost_function(self):
        tokens = super().getTokens()
        p = 1
        for t in tokens:
            p *= t.getAmount()
        return p
    
    def price_function(self, token):
        tokens = super().getTokens()
        p = 1
        for t in tokens:
            if t != token:
                p *= t.getAmount()
        return p
    


# In[4]:


class ConstantProduct_swap(ConstantProduct,Swap):
    def __init__(self, token : [Token]):
        ConstantProduct.__init__(self, token)
        k = self.cost_function()
        Swap.__init__(self, k)
        
    def token1RelativePrice(self):
        tokens = ConstantProduct.getTokens(self)
        return ConstantProduct.price_function(self, tokens[0]) / ConstantProduct.price_function(self, tokens[1])
    def token2RelativePrice(self):
        tokens = ConstantProduct.getTokens(self)
        return ConstantProduct.price_function(self, tokens[1]) / ConstantProduct.price_function(self, tokens[0])
        
    def unknownAmount(self, n):
        return Swap.getK(self) / n
    
    def valueAsset0(self, token):
        initial = ConstantProduct.getInitialState(self)
        for i in initial:
            if i.getName() == token.getName():
                return 2 * i.getAmount()
    def valueAssetN(self, token):
        return 2 * token.getAmount()
    def valueAssetRelative(self, token):
        tokens = ConstantProduct.getTokens(self)
        initial = ConstantProduct.getInitialState(self)
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
        tokens = ConstantProduct.getTokens(self)
        initial = ConstantProduct.getInitialState(self)
        #return self.valueAssetN(token) - self.valueAssetRelative(token)
        if token == tokens[0]:
            t = tokens[1]
            i = initial[1]
        else:
            t = tokens[0]
            i = initial[0]
        return (2 - (i.getAmount()/t.getAmount()))*(Swap.getK(self)/t.getAmount()) - (Swap.getK(self)/i.getAmount())
            
    def swap(self, action, token_name, quantity):
        tokens = ConstantProduct.getTokens(self)
        tradeToken = ConstantProduct.getTokenByName(self, token_name)
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

