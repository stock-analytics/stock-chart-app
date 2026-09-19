from abc import ABC, abstractmethod
from datetime import date
from ..models import ProviderResult
class Provider(ABC):
 @abstractmethod
 def fetch_daily(self,symbol:str,start_inclusive:date,end_exclusive:date)->ProviderResult: ...
