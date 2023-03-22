from abc import ABCMeta, abstractmethod

class Port:
    __metaclass__ = ABCMeta

    @abstractmethod 
    def __init__(self,port_number,port_type):
        pass

    @abstractmethod
    def on(self):
        pass

    @abstractmethod
    def off(self):
        pass

    @abstractmethod
    def toggle(self):
        pass
    
    @abstractmethod
    def set(self,value):
        pass
    
    @abstractmethod
    def read(self):
        pass


