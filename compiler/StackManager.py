class StackManager:
    def __init__(self):
        self.current_sp = 0
        self.stack = []

    def getCurrent(self):
        return self.current_sp

    def push(self, type_):
        self.stack.append(type_)
        self.current_sp += type_.getWords() * 4
    
    def pop(self):
        item = self.stack.pop()
        self.current_sp -= item.getWords() * 4

        if self.current_sp < 0:
            raise Exception("stack issue")

        return item.getWords() * 4
    
    def popItems(self, items):
        amount = 0

        for _ in range(items):
            amount += self.pop()
        
        return amount

    def popUntil(self, sp):
        amount = 0
        while sp != self.current_sp:
            amount += self.pop()

        return amount
    



