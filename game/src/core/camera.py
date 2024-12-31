"""
Oyun kamera sistemi.
"""

import pygame
from typing import Tuple

class Camera:
    def __init__(self, screen_width: int, screen_height: int):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.drag_start = None
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        
    def handle_input(self, events: list):
        """Kamera kontrollerini işler"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            # Mouse tekerleği ile zoom
            if event.type == pygame.MOUSEWHEEL:
                old_zoom = self.zoom
                self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom + event.y * 0.1))
                
                # Zoom yaparken mouse pozisyonunu merkez al
                if self.zoom != old_zoom:
                    zoom_diff = self.zoom - old_zoom
                    self.x -= (mouse_pos[0] - self.screen_width/2) * zoom_diff
                    self.y -= (mouse_pos[1] - self.screen_height/2) * zoom_diff
            
            # Mouse orta tuş ile sürükleme
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Orta tuş
                self.drag_start = mouse_pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                self.drag_start = None
            elif event.type == pygame.MOUSEMOTION and self.drag_start:
                dx = mouse_pos[0] - self.drag_start[0]
                dy = mouse_pos[1] - self.drag_start[1]
                self.x += dx
                self.y += dy
                self.drag_start = mouse_pos
    
    def apply(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Dünya koordinatlarını ekran koordinatlarına çevirir"""
        screen_x = (pos[0] * self.zoom + self.x)
        screen_y = (pos[1] * self.zoom + self.y)
        return screen_x, screen_y
    
    def unapply(self, screen_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Ekran koordinatlarını dünya koordinatlarına çevirir"""
        world_x = (screen_pos[0] - self.x) / self.zoom
        world_y = (screen_pos[1] - self.y) / self.zoom
        return world_x, world_y 