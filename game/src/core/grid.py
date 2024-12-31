"""
İzometrik grid sistemi için temel sınıflar.
"""

import pygame
from typing import Tuple
from engine.core import GameObject

class IsometricGrid:
    """İzometrik grid sistemi"""
    def __init__(self, tile_width: int = 64, tile_height: int = 32):
        self.tile_width = tile_width
        self.tile_height = tile_height
        
    def cart_to_iso(self, x: float, y: float) -> Tuple[float, float]:
        """Kartezyen koordinatları izometrik koordinatlara çevirir"""
        iso_x = (x - y) * self.tile_width / 2
        iso_y = (x + y) * self.tile_height / 2
        return iso_x, iso_y
    
    def iso_to_cart(self, screen_x: float, screen_y: float) -> Tuple[int, int]:
        """Ekran koordinatlarını grid koordinatlarına çevirir"""
        # İzometrik koordinatları kartezyen koordinatlara çevir
        cart_x = (screen_x / (self.tile_width/2) + screen_y / (self.tile_height/2)) / 2
        cart_y = (screen_y / (self.tile_height/2) - screen_x / (self.tile_width/2)) / 2
        
        # En yakın grid koordinatlarına yuvarla
        return int(round(cart_x)), int(round(cart_y))

class Tile(GameObject):
    """Tek bir grid karesi"""
    def __init__(self, grid_x: int, grid_y: int, grid: IsometricGrid):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid = grid
        self.walkable = True
        self.occupied = False
        
        # Karo rengi ve boyutu
        self.color = (100, 200, 100)  # Açık yeşil
        self.highlight_color = (255, 255, 0)  # Sarı vurgu
        
    def get_screen_pos(self) -> Tuple[float, float]:
        """Karonun ekran pozisyonunu hesaplar"""
        return self.grid.cart_to_iso(self.grid_x, self.grid_y)
    
    def render(self, surface):
        """Karoyu çizer"""
        screen_x, screen_y = self.get_screen_pos()
        
        # İzometrik karo köşe noktaları
        points = [
            (screen_x, screen_y + self.grid.tile_height/2),  # Üst
            (screen_x + self.grid.tile_width/2, screen_y),   # Sağ
            (screen_x, screen_y - self.grid.tile_height/2),  # Alt
            (screen_x - self.grid.tile_width/2, screen_y)    # Sol
        ]
        
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 1)  # Kenar çizgisi
        
    def render_highlight(self, surface):
        """Seçili karoyu vurgulu çizer"""
        screen_x, screen_y = self.get_screen_pos()
        points = [
            (screen_x, screen_y + self.grid.tile_height/2),
            (screen_x + self.grid.tile_width/2, screen_y),
            (screen_x, screen_y - self.grid.tile_height/2),
            (screen_x - self.grid.tile_width/2, screen_y)
        ]
        pygame.draw.polygon(surface, self.highlight_color, points, 3)  # Kalın vurgu çizgisi 