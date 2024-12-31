import time
import logging
import traceback
from enum import Enum
from typing import Dict, List, Optional
import sys
from dataclasses import dataclass
from datetime import datetime

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class PerformanceMetric:
    start_time: float
    end_time: float = 0
    duration: float = 0
    name: str = ""
    
class DebugSystem:
    def __init__(self):
        self.performance_metrics: Dict[str, List[PerformanceMetric]] = {}
        self.active_metrics: Dict[str, PerformanceMetric] = {}
        
        # Logging ayarları
        self.logger = logging.getLogger('GameEngine')
        self.logger.setLevel(logging.DEBUG)
        
        # Konsol handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Dosya handler
        file_handler = logging.FileHandler(f'game_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Format belirleme
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def start_metric(self, name: str) -> None:
        """Performans metriği ölçümünü başlatır"""
        self.active_metrics[name] = PerformanceMetric(
            start_time=time.perf_counter(),
            name=name
        )
    
    def end_metric(self, name: str) -> None:
        """Performans metriği ölçümünü bitirir"""
        if name in self.active_metrics:
            metric = self.active_metrics[name]
            metric.end_time = time.perf_counter()
            metric.duration = metric.end_time - metric.start_time
            
            if name not in self.performance_metrics:
                self.performance_metrics[name] = []
            
            self.performance_metrics[name].append(metric)
            del self.active_metrics[name]
    
    def get_average_duration(self, name: str) -> Optional[float]:
        """Belirli bir metrik için ortalama süreyi döndürür"""
        if name in self.performance_metrics and self.performance_metrics[name]:
            durations = [m.duration for m in self.performance_metrics[name]]
            return sum(durations) / len(durations)
        return None
    
    def log(self, level: LogLevel, message: str, exc_info=None) -> None:
        """Belirtilen seviyede log kaydı oluşturur"""
        if exc_info:
            self.logger.log(
                getattr(logging, level.value),
                f"{message}\n{traceback.format_exc()}",
                exc_info=exc_info
            )
        else:
            self.logger.log(getattr(logging, level.value), message)
    
    def clear_metrics(self) -> None:
        """Tüm performans metriklerini temizler"""
        self.performance_metrics.clear()
        self.active_metrics.clear()
    
    def get_performance_report(self) -> str:
        """Tüm performans metrikleri için detaylı rapor oluşturur"""
        report = ["Performans Raporu:"]
        for name, metrics in self.performance_metrics.items():
            if metrics:
                avg_duration = self.get_average_duration(name)
                min_duration = min(m.duration for m in metrics)
                max_duration = max(m.duration for m in metrics)
                report.append(f"\n{name}:")
                report.append(f"  Ortalama: {avg_duration:.6f} sn")
                report.append(f"  Minimum: {min_duration:.6f} sn")
                report.append(f"  Maximum: {max_duration:.6f} sn")
                report.append(f"  Ölçüm Sayısı: {len(metrics)}")
        
        return "\n".join(report)

# Global debug instance
debug_system = DebugSystem() 