"""
Debug sistemi.
Performans izleme, hata ayıklama ve geliştirici araçlarını içerir.
"""

import time
import pygame
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto
from ..core.base import GameSystem

class DebugLevel(Enum):
    """Debug seviyeleri"""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

class DebugSystem(GameSystem):
    """Debug sistemi"""
    
    def __init__(self):
        super().__init__("DebugSystem")
        self.enabled = True
        self.show_fps = True
        self.show_memory = True
        self.show_physics = True
        
        # FPS hesaplama için değişkenler
        self.fps_font = None
        self.frame_times: List[float] = []
        self.max_frame_samples = 30
        self.last_time = time.time()
        
        # Debug mesajları
        self.messages: List[Tuple[str, DebugLevel, float]] = []
        self.message_lifetime = 5.0
        
        # Performans metrikleri
        self.performance_metrics: Dict[str, float] = {
            "update_time": 0.0,
            "render_time": 0.0,
            "physics_time": 0.0
        }
        
    def initialize(self):
        """Debug sistemini başlatır"""
        try:
            self.fps_font = pygame.font.SysFont("monospace", 16)
        except:
            print("Debug font yüklenemedi!")
            
    def log(self, message: str, level: DebugLevel = DebugLevel.INFO):
        """Debug mesajı ekler"""
        if not self.enabled:
            return
            
        self.messages.append((message, level, time.time()))
        
        # Eski mesajları temizle
        current_time = time.time()
        self.messages = [(msg, lvl, t) for msg, lvl, t in self.messages 
                        if current_time - t < self.message_lifetime]
                        
    def update_fps(self):
        """FPS bilgisini günceller"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_frame_samples:
            self.frame_times.pop(0)
            
    def get_fps(self) -> float:
        """Ortalama FPS değerini döndürür"""
        if not self.frame_times:
            return 0.0
        return len(self.frame_times) / sum(self.frame_times)
        
    def start_profile(self, name: str):
        """Performans profillemesini başlatır"""
        if not self.enabled:
            return
        self.performance_metrics[f"{name}_start"] = time.time()
        
    def end_profile(self, name: str):
        """Performans profillemesini bitirir"""
        if not self.enabled:
            return
        if f"{name}_start" in self.performance_metrics:
            elapsed = time.time() - self.performance_metrics[f"{name}_start"]
            self.performance_metrics[name] = elapsed
            
    def draw(self, surface: pygame.Surface):
        """Debug bilgilerini çizer"""
        if not self.enabled or not self.fps_font:
            return
            
        y_offset = 10
        x_offset = 10
        line_height = 20
        
        # FPS göster
        if self.show_fps:
            fps_text = f"FPS: {self.get_fps():.1f}"
            fps_surface = self.fps_font.render(fps_text, True, (255, 255, 255))
            surface.blit(fps_surface, (x_offset, y_offset))
            y_offset += line_height
            
        # Performans metriklerini göster
        if self.show_memory:
            for name, value in self.performance_metrics.items():
                if not name.endswith("_start"):
                    metric_text = f"{name}: {value*1000:.1f}ms"
                    metric_surface = self.fps_font.render(metric_text, True, (255, 255, 255))
                    surface.blit(metric_surface, (x_offset, y_offset))
                    y_offset += line_height
                    
        # Debug mesajlarını göster
        current_time = time.time()
        for msg, level, t in self.messages:
            if current_time - t < self.message_lifetime:
                # Seviyeye göre renk belirle
                color = {
                    DebugLevel.INFO: (255, 255, 255),
                    DebugLevel.WARNING: (255, 255, 0),
                    DebugLevel.ERROR: (255, 0, 0)
                }[level]
                
                msg_surface = self.fps_font.render(msg, True, color)
                surface.blit(msg_surface, (x_offset, y_offset))
                y_offset += line_height
                
    def clear(self):
        """Debug verilerini temizler"""
        self.messages.clear()
        self.frame_times.clear()
        self.performance_metrics = {
            "update_time": 0.0,
            "render_time": 0.0,
            "physics_time": 0.0
        } 