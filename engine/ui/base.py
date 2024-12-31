"""
UI sistemi temel sınıfları.
Oyun içi arayüz elemanlarını içerir.
"""

import pygame
from typing import List, Optional, Tuple, Callable
from ..core.base import GameObject

class UIElement(GameObject):
    """UI elemanlarının temel sınıfı"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__("UIElement")
        self.rect = pygame.Rect(x, y, width, height)
        self.parent: Optional['UIElement'] = None
        self.children: List['UIElement'] = []
        self.visible = True
        self.enabled = True
        self.background_color = None
        self.border_color = None
        self.border_width = 0
        
    def add_child(self, child: 'UIElement'):
        """Alt eleman ekler"""
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'UIElement'):
        """Alt elemanı kaldırır"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def get_absolute_position(self) -> Tuple[int, int]:
        """Mutlak pozisyonu döndürür"""
        x, y = self.rect.x, self.rect.y
        parent = self.parent
        while parent:
            x += parent.rect.x
            y += parent.rect.y
            parent = parent.parent
        return x, y
        
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Noktanın eleman içinde olup olmadığını kontrol eder"""
        abs_x, abs_y = self.get_absolute_position()
        abs_rect = pygame.Rect(abs_x, abs_y, self.rect.width, self.rect.height)
        return abs_rect.collidepoint(point)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Olayı işler"""
        if not self.enabled:
            return False
            
        # Alt elemanlara olayı ilet
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
                
        return False
        
    def update(self, dt: float):
        """UI elemanını günceller"""
        super().update(dt)
        for child in self.children:
            child.update(dt)
            
    def draw(self, surface: pygame.Surface):
        """UI elemanını çizer"""
        if not self.visible:
            return
            
        # Arkaplan
        if self.background_color:
            pygame.draw.rect(surface, self.background_color, self.rect)
            
        # Kenarlık
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
            
        # Alt elemanları çiz
        for child in self.children:
            child.draw(surface)

class Button(UIElement):
    """Buton sınıfı"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str = ""):
        super().__init__(x, y, width, height)
        self.text = text
        self.font: Optional[pygame.font.Font] = None
        self.text_color = (0, 0, 0)
        self.hover_color = None
        self.pressed_color = None
        self.on_click: Optional[Callable[[], None]] = None
        self.is_hovered = False
        self.is_pressed = False
        
    def set_font(self, font: pygame.font.Font):
        """Yazı fontunu ayarlar"""
        self.font = font
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Buton olaylarını işler"""
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.contains_point(event.pos)
            return self.is_hovered
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos):
                self.is_pressed = True
                return True
                
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if was_pressed and self.contains_point(event.pos):
                if self.on_click:
                    self.on_click()
                return True
                
        return False
        
    def draw(self, surface: pygame.Surface):
        """Butonu çizer"""
        if not self.visible:
            return
            
        # Arkaplan rengi
        color = self.background_color
        if self.is_pressed and self.pressed_color:
            color = self.pressed_color
        elif self.is_hovered and self.hover_color:
            color = self.hover_color
            
        if color:
            abs_x, abs_y = self.get_absolute_position()
            abs_rect = pygame.Rect(abs_x, abs_y, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, color, abs_rect)
            
        # Kenarlık
        if self.border_color and self.border_width > 0:
            abs_x, abs_y = self.get_absolute_position()
            abs_rect = pygame.Rect(abs_x, abs_y, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
            
        # Metin
        if self.text and self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            abs_x, abs_y = self.get_absolute_position()
            text_rect = text_surface.get_rect(center=(abs_x + self.rect.width // 2,
                                                    abs_y + self.rect.height // 2))
            surface.blit(text_surface, text_rect)

class Panel(UIElement):
    """Panel sınıfı"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.padding = 0
        
    def auto_layout(self, spacing: int = 5):
        """Alt elemanları otomatik düzenler"""
        current_y = self.padding
        for child in self.children:
            child.rect.x = self.padding
            child.rect.y = current_y
            child.rect.width = self.rect.width - 2 * self.padding
            current_y += child.rect.height + spacing
            
    def set_padding(self, padding: int):
        """Kenar boşluğunu ayarlar"""
        self.padding = padding 