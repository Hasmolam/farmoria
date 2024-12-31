import pygame
from enum import Enum

class Alignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class UIElement:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        self.children = []
        self.parent = None
    
    def get_absolute_position(self):
        """UI elemanının ekrandaki mutlak konumunu hesapla"""
        x, y = self.x, self.y
        current = self.parent
        while current:
            x += current.x
            y += current.y
            current = current.parent
        return (x, y)
    
    def contains_point(self, point: tuple) -> bool:
        """Verilen nokta UI elemanının içinde mi kontrol et"""
        mouse_x, mouse_y = point
        abs_x, abs_y = self.get_absolute_position()
        return (abs_x <= mouse_x <= abs_x + self.width and
                abs_y <= mouse_y <= abs_y + self.height)
    
    def add_child(self, child):
        """Çocuk eleman ekle"""
        child.parent = self
        self.children.append(child)
    
    def draw(self, surface: pygame.Surface):
        """UI elemanını çiz"""
        if not self.visible:
            return
        
        # Kendini çiz
        self._draw_self(surface)
        
        # Çocukları çiz
        for child in self.children:
            child.draw(surface)
    
    def handle_event(self, event: pygame.event.Event):
        """Olay işleme"""
        if not self.visible or not self.enabled:
            return False
        
        # Önce çocukların olaylarını işle (son eklenen ilk işlenir)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Kendi olayını işle
        return self._handle_self_event(event)
    
    def _draw_self(self, surface: pygame.Surface):
        pass
    
    def _handle_self_event(self, event: pygame.event.Event) -> bool:
        return False

class Panel(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 bg_color=(50, 50, 50), border_color=None):
        super().__init__(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
    
    def _draw_self(self, surface: pygame.Surface):
        abs_x, abs_y = self.get_absolute_position()
        # Panel arka planı
        pygame.draw.rect(surface, self.bg_color,
                        (abs_x, abs_y, self.width, self.height))
        
        # Kenarlık
        if self.border_color:
            pygame.draw.rect(surface, self.border_color,
                           (abs_x, abs_y, self.width, self.height), 1)

class Label(UIElement):
    def __init__(self, x: int, y: int, text: str,
                 color=(255, 255, 255), font_size=32,
                 alignment=Alignment.LEFT):
        super().__init__(x, y, 0, 0)  # Boyutlar sonra ayarlanacak
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.alignment = alignment
        
        # Boyutları hesapla
        self._update_size()
    
    def _update_size(self):
        text_surface = self.font.render(self.text, True, self.color)
        self.width = text_surface.get_width()
        self.height = text_surface.get_height()
    
    def _draw_self(self, surface: pygame.Surface):
        text_surface = self.font.render(self.text, True, self.color)
        abs_x, abs_y = self.get_absolute_position()
        
        if self.alignment == Alignment.CENTER:
            x = abs_x - text_surface.get_width() // 2
        elif self.alignment == Alignment.RIGHT:
            x = abs_x - text_surface.get_width()
        else:
            x = abs_x
            
        surface.blit(text_surface, (x, abs_y))

class Button(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str = "",
                 text_color: tuple = (255, 255, 255),
                 bg_color: tuple = (100, 100, 100),
                 hover_color: tuple = None,
                 font_size: int = 24,
                 callback = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color or tuple(min(c + 30, 255) for c in bg_color)
        self.font = pygame.font.Font(None, font_size)
        self.callback = callback
        self.is_hovered = False
    
    def _draw_self(self, surface: pygame.Surface):
        abs_x, abs_y = self.get_absolute_position()
        # Arka plan
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, (abs_x, abs_y, self.width, self.height))
        
        # Metin
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(abs_x + self.width//2,
                                                abs_y + self.height//2))
        surface.blit(text_surface, text_rect)
    
    def _handle_self_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.contains_point(event.pos)
            return self.is_hovered
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()
                return True
        
        return False 