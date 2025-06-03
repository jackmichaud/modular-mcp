import json
from typing import Any, Optional
from datetime import datetime, timedelta

class ResultCache:
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.max_size = max_size
    
    def set(self, key: str, value: Any, ttl: int = 300):
        if len(self.cache) >= self.max_size:
            pass