from abc import ABC, abstractmethod

# 各予測処理のインターフェース
class BaseModel(ABC):
    
    @abstractmethod
    def train(self, df):
        pass

    @abstractmethod
    def predict(self, df, param):
        pass