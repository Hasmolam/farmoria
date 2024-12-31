"""Debug sistemi için temel sınıflar ve fonksiyonlar."""

import logging
import time
from enum import Enum
from typing import Dict, Any, Optional
import pygame

class DebugLevel(Enum):
    """Debug seviyelerini tanımlar."""
    NONE = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    DEBUG = 4

class DebugCategory(Enum):
    """Debug kategorilerini tanımlar."""
    RESOURCE = "resource"
    ANIMATION = "animation"
    SHADER = "shader"
    PHYSICS = "physics"
    RENDER = "render"
    AUDIO = "audio"
    INPUT = "input"
    NETWORK = "network"

class DebugManager:
    """Debug yönetim sistemi."""
    
    def __init__(self):
        self.enabled = True
        self.level = DebugLevel.INFO
        self.categories = {cat: True for cat in DebugCategory}
        self.logs = []
        self.performance_metrics = {}
        self.frame_times = []
        self.max_logs = 1000
        
        # Logging ayarları
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='game_debug.log'
        )
        self.logger = logging.getLogger('GameEngine')
    
    def log(self, category: DebugCategory, level: DebugLevel, message: str, data: Dict[str, Any] = None):
        """Debug mesajı kaydet."""
        if not self.enabled or not self.categories[category] or level.value <= self.level.value:
            return
            
        log_entry = {
            'timestamp': time.time(),
            'category': category.value,
            'level': level.value,
            'message': message,
            'data': data or {}
        }
        
        self.logs.append(log_entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
            
        # Logging seviyesine göre kaydet
        if level == DebugLevel.ERROR:
            self.logger.error(message, extra={'data': data})
        elif level == DebugLevel.WARNING:
            self.logger.warning(message, extra={'data': data})
        elif level == DebugLevel.INFO:
            self.logger.info(message, extra={'data': data})
        else:
            self.logger.debug(message, extra={'data': data})
    
    def start_performance_metric(self, name: str):
        """Performans metriği ölçümü başlat."""
        self.performance_metrics[name] = {
            'start_time': time.perf_counter(),
            'samples': [],
            'min': float('inf'),
            'max': float('-inf'),
            'avg': 0
        }
    
    def end_performance_metric(self, name: str):
        """Performans metriği ölçümü bitir."""
        if name not in self.performance_metrics:
            return
            
        duration = time.perf_counter() - self.performance_metrics[name]['start_time']
        metrics = self.performance_metrics[name]
        metrics['samples'].append(duration)
        
        # İstatistikleri güncelle
        metrics['min'] = min(metrics['min'], duration)
        metrics['max'] = max(metrics['max'], duration)
        metrics['avg'] = sum(metrics['samples']) / len(metrics['samples'])
    
    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Performans istatistiklerini döndür."""
        return {
            name: {
                'min': metrics['min'],
                'max': metrics['max'],
                'avg': metrics['avg'],
                'samples': len(metrics['samples'])
            }
            for name, metrics in self.performance_metrics.items()
        }
    
    def update_frame_time(self, dt: float):
        """Kare süresini güncelle."""
        self.frame_times.append(dt)
        if len(self.frame_times) > 100:
            self.frame_times.pop(0)
    
    def get_fps(self) -> float:
        """Ortalama FPS değerini döndür."""
        if not self.frame_times:
            return 0
        return 1.0 / (sum(self.frame_times) / len(self.frame_times))
    
    def draw_debug_overlay(self, surface: pygame.Surface):
        """Debug bilgilerini ekrana çiz."""
        if not self.enabled:
            return
            
        font = pygame.font.Font(None, 24)
        y = 10
        
        # FPS göster
        fps_text = f"FPS: {self.get_fps():.1f}"
        text_surface = font.render(fps_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, y))
        y += 30
        
        # Performans metrikleri
        for name, stats in self.get_performance_stats().items():
            metric_text = f"{name}: {stats['avg']*1000:.2f}ms"
            text_surface = font.render(metric_text, True, (255, 255, 255))
            surface.blit(text_surface, (10, y))
            y += 20
        
        # Son logları göster
        y += 20
        for log in self.logs[-5:]:
            color = (255, 255, 255)
            if log['level'] == DebugLevel.ERROR.value:
                color = (255, 0, 0)
            elif log['level'] == DebugLevel.WARNING.value:
                color = (255, 255, 0)
                
            log_text = f"{log['category']}: {log['message']}"
            text_surface = font.render(log_text, True, color)
            surface.blit(text_surface, (10, y))
            y += 20
    
    def clear(self):
        """Debug verilerini temizle."""
        self.logs.clear()
        self.performance_metrics.clear()
        self.frame_times.clear()

# Global debug manager instance
debug_manager = DebugManager() 