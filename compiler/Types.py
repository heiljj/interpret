class BaseType:
    def __init__(self, name, words):
        self.name = name
        self.words = words
    
    def __eq__(self, o):
        return self.name == o.name and self.words == o.words
    
    def __ne__(self, o):
        return not self == o
    
    def getWords(self):
        return self.words
    
    def getAllocWords(self):
        return self.words

class PointerType(BaseType):
    def __init__(self, type_, amount=0):
        super().__init__(None, 1)
        self.type = type_
        self.amount = amount
    
    def getWords(self):
        return 1
    
    def getAllocWords(self):
        if self.amount:
            return int(self.type.getWords() * self.amount)
        
        return 1

    
    def getPointedWords(self):
        return self.type.getWords()
    
    def __eq__(self, o):
        if type(o) != PointerType:
            return False
        
        return self.type == o.type
    
    def __ne__(self, o):
        return not self == o

class StructType(BaseType):
    def __init__(self, properties, property_types):
        if len(properties) != len(property_types):
            raise Exception

        self.properties = properties 
        self.property_types = property_types
        self.property_word_offsets = {}

        s = 0
        for i in range(len(self.properties)):
            self.property_word_offsets[self.properties[i]] = s
            s += self.property_types[i].getWords()
        
        super().__init__(None, s)
    
    def getPropertyType(self, name):
        return self.property_types[self.properties.index(name)]
    
    def getPropertyOffset(self, name):
        return self.property_word_offsets[name]
    
    def getPropertySize(self, name):
        return self.getPropertySize(name).getWords()
    
    def __eq__(self, o):
        if not type(o) == UnknownStructType and not type(o) == StructType:
            return False
        
        if len(self.property_types) != len(o.property_types):
            return False
        
        return self.property_types == o.property_types
    
    def __ne__(self, o):
        return not self == o

class UnknownStructType(StructType):
    def __init__(self, property_types):
        super().__init__([None for _ in range(len(property_types))], property_types)
    