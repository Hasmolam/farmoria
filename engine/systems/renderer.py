import pygame
from typing import Dict, List, Optional
from ..core.base import GameObject, GameSystem
from enum import Enum, auto

class RenderLayer(Enum):
    """Render katmanları"""
    BACKGROUND = auto()
    MIDDLE = auto()
    TOP = auto()

class RenderObject:
    """Render edilebilir nesne"""
    def __init__(self, surface, x=0, y=0, layer=RenderLayer.MIDDLE):
        """RenderObject başlatıcı"""
        self.surface = surface
        self.x = x
        self.y = y
        self.layer = layer
        self.visible = True
        self.z_index = 0
        self.rect: Optional[pygame.Rect] = None
        
    def set_surface(self, surface: pygame.Surface):
        """Render yüzeyini ayarlar"""
        self.surface = surface
        self.rect = surface.get_rect()
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
    def render(self, surface: pygame.Surface):
        """Nesneyi render eder"""
        if self.surface and self.rect:
            surface.blit(self.surface, self.rect)

class Renderer:
    """Render sınıfı"""
    
    def __init__(self, screen):
        """Renderer başlatıcı"""
        self.screen = screen
        self.layers = {layer: [] for layer in RenderLayer}
        
    def add_object(self, obj):
        """Nesne ekler"""
        self.layers[obj.layer].append(obj)
        
    def remove_object(self, obj):
        """Nesne siler"""
        if obj in self.layers[obj.layer]:
            self.layers[obj.layer].remove(obj)
            
    def clear_layer(self, layer):
        """Katmanı temizler"""
        self.layers[layer].clear()
        
    def clear_all(self):
        """Tüm katmanları temizler"""
        for layer in self.layers.values():
            layer.clear()
            
    def draw(self):
        """Tüm nesneleri çizer"""
        for layer in RenderLayer:
            for obj in self.layers[layer]:
                if obj.visible:
                    self.screen.blit(obj.surface, (obj.x, obj.y)) 