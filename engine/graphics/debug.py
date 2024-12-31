import pygame
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import logging

class DebugCategory(Enum):
    """Debug kategorileri"""
    GENERAL = auto()
    PHYSICS = auto()
    GRAPHICS = auto()
    SHADER = auto()
    AUDIO = auto()
    INPUT = auto()
    NETWORK = auto()
    AI = auto()

class DebugLevel(Enum):
    """Debug seviyeleri"""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

class DebugManager:
    """Debug yönetim sistemi"""
    def __init__(self):
        self.enabled = True
        self.messages: Dict[DebugCategory, List[Tuple[str, DebugLevel, float]]] = {
            category: [] for category in DebugCategory
        }
        self.message_lifetime = 5.0  # Mesajların ekranda kalma süresi
        self.max_messages = 10  # Her kategori için maksimum mesaj sayısı
        self.colors = {
            DebugLevel.INFO: (255, 255, 255),     # Beyaz
            DebugLevel.WARNING: (255, 255, 0),    # Sarı
            DebugLevel.ERROR: (255, 0, 0)         # Kırmızı
        }
        
        # Logging ayarları
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('debug.log'),
                logging.StreamHandler()
            ]
        )
        
    def log(self, message: str, category: DebugCategory = DebugCategory.GENERAL, 
            level: DebugLevel = DebugLevel.INFO, lifetime: Optional[float] = None):
        """Debug mesajı ekler"""
        if not self.enabled:
            return
            
        # Logging
        if level == DebugLevel.ERROR:
            logging.error(f"[{category.name}] {message}")
        elif level == DebugLevel.WARNING:
            logging.warning(f"[{category.name}] {message}")
        else:
            logging.info(f"[{category.name}] {message}")
            
        # Mesajı listeye ekle
        if category not in self.messages:
            self.messages[category] = []
            
        messages = self.messages[category]
        messages.append((message, level, lifetime or self.message_lifetime))
        
        # Maksimum mesaj sayısını kontrol et
        if len(messages) > self.max_messages:
            messages.pop(0)
            
    def update(self, dt: float):
        """Debug mesajlarını günceller"""
        if not self.enabled:
            return
            
        # Her kategorideki mesajları güncelle
        for category in DebugCategory:
            messages = self.messages[category]
            i = 0
            while i < len(messages):
                message, level, lifetime = messages[i]
                lifetime -= dt
                if lifetime <= 0:
                    messages.pop(i)
                else:
                    messages[i] = (message, level, lifetime)
                    i += 1
                    
    def draw(self, surface: pygame.Surface):
        """Debug mesajlarını çizer"""
        if not self.enabled:
            return
            
        # Font'u her çizimde oluştur
        font = pygame.font.Font(None, 24)
            
        y = 10
        for category in DebugCategory:
            messages = self.messages[category]
            if messages:
                # Kategori başlığını çiz
                category_text = font.render(f"=== {category.name} ===", True, (200, 200, 200))
                surface.blit(category_text, (10, y))
                y += 25
                
                # Mesajları çiz
                for message, level, _ in messages:
                    color = self.colors[level]
                    text = font.render(message, True, color)
                    surface.blit(text, (20, y))
                    y += 20
                y += 5  # Kategoriler arası boşluk
                
    def clear(self, category: Optional[DebugCategory] = None):
        """Debug mesajlarını temizler"""
        if category:
            self.messages[category].clear()
        else:
            for messages in self.messages.values():
                messages.clear()
                
    def set_enabled(self, enabled: bool):
        """Debug sistemini aktif/pasif yapar"""
        self.enabled = enabled
        
    def is_enabled(self) -> bool:
        """Debug sisteminin aktif olup olmadığını döndürür"""
        return self.enabled

    def start_performance_metric(self, name: str):
        """Performans metriği başlatır"""
        if not hasattr(self, 'performance_metrics'):
            self.performance_metrics = {}
        self.performance_metrics[name] = pygame.time.get_ticks()

    def end_performance_metric(self, name: str) -> Optional[float]:
        """Performans metriğini sonlandırır ve geçen süreyi döndürür"""
        if not hasattr(self, 'performance_metrics') or name not in self.performance_metrics:
            return None
        
        end_time = pygame.time.get_ticks()
        start_time = self.performance_metrics[name]
        duration = (end_time - start_time) / 1000.0  # saniyeye çevir
        
        self.log(
            f"Performans metriği: {name} = {duration:.3f}s",
            category=DebugCategory.GENERAL,
            level=DebugLevel.INFO
        )
        
        del self.performance_metrics[name]
        return duration

    def get_performance_stats(self) -> Dict[str, float]:
        """Aktif performans metriklerini döndürür"""
        if not hasattr(self, 'performance_metrics'):
            return {}
        
        current_time = pygame.time.get_ticks()
        return {
            name: (current_time - start_time) / 1000.0
            for name, start_time in self.performance_metrics.items()
        }

# Singleton instance
debug_manager = DebugManager() 