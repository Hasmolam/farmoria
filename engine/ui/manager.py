"""
UI yönetim sistemi.
UI elemanlarının yönetimini ve olayların işlenmesini sağlar.
"""

import pygame
from typing import List, Optional
from ..core.base import GameSystem
from .base import UIElement

class UIManager(GameSystem):
    """UI yönetim sistemi"""
    
    def __init__(self):
        super().__init__("UIManager")
        self.root = UIElement(0, 0, 0, 0)  # Kök eleman
        self.focused_element: Optional[UIElement] = None
        self.default_font: Optional[pygame.font.Font] = None
        
    def initialize(self, screen_width: int, screen_height: int):
        """UI sistemini başlatır"""
        self.root.rect.width = screen_width
        self.root.rect.height = screen_height
        try:
            self.default_font = pygame.font.SysFont("arial", 16)
        except:
            print("Varsayılan font yüklenemedi!")
            
    def add_element(self, element: UIElement):
        """UI elemanı ekler"""
        self.root.add_child(element)
        
    def remove_element(self, element: UIElement):
        """UI elemanı kaldırır"""
        self.root.remove_child(element)
        if self.focused_element == element:
            self.focused_element = None
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """UI olaylarını işler"""
        if not self.enabled:
            return False
            
        # Fare olayları için eleman bul
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            element = self.get_element_at(event.pos)
            if element:
                return element.handle_event(event)
                
        # Odaklanmış eleman varsa ona gönder
        if self.focused_element:
            return self.focused_element.handle_event(event)
            
        return False
        
    def update(self, dt: float):
        """UI sistemini günceller"""
        self.root.update(dt)
        
    def draw(self, surface: pygame.Surface):
        """UI sistemini çizer"""
        self.root.draw(surface)
        
    def get_element_at(self, position) -> Optional[UIElement]:
        """Belirli bir konumdaki UI elemanını bulur"""
        def _find_element(element: UIElement) -> Optional[UIElement]:
            # Önce alt elemanları kontrol et (üsttekiler önce)
            for child in reversed(element.children):
                if child.visible and child.enabled:
                    found = _find_element(child)
                    if found:
                        return found
                        
            # Kendini kontrol et
            if element.contains_point(position):
                return element
                
            return None
            
        # Kök elemandan başlayarak ara
        found = _find_element(self.root)
        # Kök elemanı döndürme
        return found if found != self.root else None
        
    def set_focus(self, element: Optional[UIElement]):
        """Odaklanmayı ayarlar"""
        if self.focused_element != element:
            self.focused_element = element 