from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import json

@dataclass
class ToolMetrics:
    name: str
    calls: int
    avg_response_time: float
    errors: int

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, ToolMetrics] = {}
        self.response_times: Dict[str, List[float]] = {}
    
    def record_call(self, tool_name: str, response_time: float, success: bool):
        if tool_name not in self.metrics:
            self.metrics[tool_name] = ToolMetrics(tool_name, 0, 0.0, 0)
            self.response_times[tool_name] = []
        
        self.metrics[tool_name].calls += 1
        if not success:
            self.metrics[tool_name].errors += 1
        
        self.response_times[tool_name].append(response_time)
        self.metrics[tool_name].avg_response_time = (
            sum(self.response_times[tool_name]) / 
            len(self.response_times[tool_name])
        )
    
    def get_metrics(self) -> Dict:
        return {
            name: {
                "calls": metric.calls,
                "avg_response_time": metric.avg_response_time,
                "errors": metric.errors
            }
            for name, metric in self.metrics.items()
        }