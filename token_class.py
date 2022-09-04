class Token:
    def __init__(self, name, amount, weight = 0.5):
        self.__name = name
        self.__amount = amount
        self.__weight = weight
        
    def getName(self):
        return self.__name
    def getAmount(self):
        return self.__amount
    def setAmount(self,amount):
        self.__amount = amount
    def getWeight(self):
        return self.__weight

