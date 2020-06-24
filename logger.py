from abc import ABC, abstractmethod
from datetime import datetime


class AbstractLogger(ABC):
    @abstractmethod
    def log(self, msg):
        pass


class FileLogger(AbstractLogger):
    def __init__(self, filename='log.txt'):
        self.filename = filename
    
    def log(self, msg):
        with open(self.filename, 'a') as log:
            log.write(f'{datetime.now()}: {msg}\n')