class BaseType:
    def __init__(self, name, words):
        self.name = name
        self.words = words
    
    def __eq__(self, o):
        return self.name == o.name 
    
    def __str__(self):
        return str(self.name)
    
    def getWords(self):
        return self.words
    
    def equiv(self, o):
        return self == o

class StructType:
    def __init__(self, name, properties, property_types):
        if len(properties) != len(property_types):
            raise Exception

        self.name = name
        self.properties = properties
        self.property_types = property_types

        self.property_word_offsets = {}

        s = 0
        for i in range(len(self.properties)):
            self.property_word_offsets[self.properties[i]] = s
            s += self.property_types[i].getWords()
        
        self.words = s
    
    def getWords(self):
        return self.words
    
    def getPropertyType(self, name):
        return self.property_types[self.properties.index(name)]
    
    def getPropertyOffset(self, name):
        return self.property_word_offsets[name]
    
    def getPropertySize(self, name):
        return self.property_types[self.properties.index(name)].getWords()
    
    def equiv(self, o):
        if type(o) != UnknownStructType:
            return self == o
        
        if len(o.property_types) != len(self.property_types):
            return False
        
        for i in range(len(o.property_types)):
            if not o.property_types[i].equiv(self.property_types[i]):
                return False
        
        return True
    
    def __eq__(self, o):
        if type(o) == BaseType:
            return False
        # structs with the same stuff are considered equiv - this is probably fine?
        return self.property_types == o.property_types
    
    def __ne__(self, o):
        return not self == o
        
        
class UnknownStructType:
    def __init__(self, property_types):
        self.property_types = property_types
        self.words = 0

        for t in self.property_types:
            self.words += t.getWords() 
        
    def getWords(self):
        return self.words
    
    def equiv(self, o):
        if len(o.property_types) != len(self.property_types):
            return False

        for i in range(len(o.property_types)):
            if not o.property_types[i].equiv(self.property_types[i]):
                return False
        
        return True



class PointerType:
    def __init__(self, type_, amount=0):
        self.type = type_
        self.amount = amount
    
    def getWords(self):
        if self.amount:
            return self.type.getWords() * self.amount
        return 1
    
    def getPointedWords(self):
        return self.type.getWords()
    
    def __eq__(self, o):
        return self.type == o.type and self.amount == o.amount
    
    def equiv(self, o):
        return self.type == o.type
