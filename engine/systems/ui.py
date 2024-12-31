import pygame
from typing import Dict, List, Optional, Callable
from ..core.base import GameObject, GameSystem

class UIElement(GameObject):
    """UI elemanlarının temel sınıfı"""
    def __init__(self, x: int, y: int, width: int, height: int, name: str = "UIElement"):
        super().__init__(name)
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.parent: Optional[UIElement] = None
        self.children: List[UIElement] = []
        
    def add_child(self, child: 'UIElement'):
        """UI elemanına çocuk eleman ekler"""
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'UIElement'):
        """UI elemanından çocuk elemanı kaldırır"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """UI olaylarını işler"""
        if not self.enabled:
            return False
            
        # Önce çocukları kontrol et
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
                
        return False
        
    def update(self, dt: float):
        """UI elemanını günceller"""
        if not self.enabled:
            return
            
        super().update(dt)
        
        for child in self.children:
            child.update(dt)
            
    def draw(self, surface: pygame.Surface):
        """UI elemanını çizer"""
        if not self.visible:
            return
            
        super().draw(surface)
        
        for child in self.children:
            child.draw(surface)

class Button(UIElement):
    """Temel buton sınıfı"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str = "", name: str = "Button"):
        super().__init__(x, y, width, height, name)
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.color = pygame.Color("gray")
        self.hover_color = pygame.Color("darkgray")
        self.text_color = pygame.Color("black")
        self.is_hovered = False
        self.on_click: Optional[Callable[[], None]] = None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Buton olaylarını işler"""
        if not super().handle_event(event):
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos) and self.on_click:
                    self.on_click()
                    return True
        return False
        
    def draw(self, surface: pygame.Surface):
        """Butonu çizer"""
        if not self.visible:
            return
            
        # Arka planı çiz
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        
        # Metni çiz
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
            
        super().draw(surface)

class UIManager(GameSystem):
    """UI sistemini yöneten sınıf"""
    def __init__(self):
        super().__init__("UIManager")
        self.root = UIElement(0, 0, 0, 0, "Root")
        self.engine = None
        
    def set_engine(self, engine):
        """Engine referansını ayarlar"""
        self.engine = engine
        if engine and engine.screen:
            self.root.rect.size = engine.screen.get_size()
            
    def add_element(self, element: UIElement):
        """UI elemanı ekler"""
        self.root.add_child(element)
        
    def remove_element(self, element: UIElement):
        """UI elemanını kaldırır"""
        self.root.remove_child(element)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """UI olaylarını işler"""
        return self.root.handle_event(event)
        
    def update(self, dt: float):
        """UI sistemini günceller"""
        self.root.update(dt)
        
    def draw(self, surface: pygame.Surface):
        """UI sistemini çizer"""
        self.root.draw(surface) 