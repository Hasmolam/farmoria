import pygame
from typing import Dict, Optional, Tuple
import math
from ..core.base import GameObject, GameSystem
from ..systems.physics import PhysicsSystem
from ..systems.input import InputSystem
from ..graphics.animation import AnimationManager
from ..utils.debug import DebugSystem

class Player(GameObject):
    """Oyuncu sınıfı"""
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__(x, y)
        self.width = 32
        self.height = 48
        self.speed = 200
        self.velocity_x = 0
        self.velocity_y = 0
        self.animation_manager = AnimationManager()
        self.debug_manager = DebugSystem()
        self.direction = "down"
        self.is_moving = False
        
    def update(self, dt: float):
        """Oyuncuyu günceller"""
        # Pozisyonu güncelle
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Animasyonları güncelle
        self.animation_manager.update(dt)
        
        # Debug bilgilerini güncelle
        self.debug_manager.log(f"Player position: ({self.x}, {self.y})")
        self.debug_manager.log(f"Player velocity: ({self.velocity_x}, {self.velocity_y})")
        self.debug_manager.log(f"Player direction: {self.direction}")
        
    def draw(self, surface: pygame.Surface):
        """Oyuncuyu çizer"""
        current_frame = self.animation_manager.get_current_frame()
        if current_frame:
            surface.blit(current_frame, (self.x, self.y))
            
    def move(self, dx: float, dy: float):
        """Oyuncuyu hareket ettirir"""
        self.velocity_x = dx * self.speed
        self.velocity_y = dy * self.speed
        
        # Yönü güncelle
        if abs(dx) > abs(dy):
            if dx > 0:
                self.direction = "right"
            else:
                self.direction = "left"
        else:
            if dy > 0:
                self.direction = "down"
            else:
                self.direction = "up"
                
        # Hareket durumunu güncelle
        self.is_moving = dx != 0 or dy != 0
        
        # Uygun animasyonu oynat
        if self.is_moving:
            self.animation_manager.play(f"walk_{self.direction}")
        else:
            self.animation_manager.play(f"idle_{self.direction}")
            
    def stop(self):
        """Oyuncuyu durdurur"""
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        self.animation_manager.play(f"idle_{self.direction}")
        
    def get_position(self) -> Tuple[float, float]:
        """Oyuncunun pozisyonunu döndürür"""
        return self.x, self.y
        
    def get_velocity(self) -> Tuple[float, float]:
        """Oyuncunun hızını döndürür"""
        return self.velocity_x, self.velocity_y
        
    def get_direction(self) -> str:
        """Oyuncunun yönünü döndürür"""
        return self.direction
        
    def is_moving(self) -> bool:
        """Oyuncunun hareket edip etmediğini döndürür"""
        return self.is_moving
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Oyuncunun sınırlarını döndürür"""
        return self.x, self.y, self.width, self.height
        
    def collides_with(self, other: GameObject) -> bool:
        """Diğer nesne ile çarpışma kontrolü yapar"""
        x1, y1, w1, h1 = self.get_bounds()
        x2, y2, w2, h2 = other.get_bounds()
        
        return (x1 < x2 + w2 and
                x1 + w1 > x2 and
                y1 < y2 + h2 and
                y1 + h1 > y2)
                
    def handle_collision(self, other: GameObject):
        """Çarpışma durumunda yapılacak işlemleri gerçekleştirir"""
        # Çarpışma yönüne göre pozisyonu düzelt
        x1, y1, w1, h1 = self.get_bounds()
        x2, y2, w2, h2 = other.get_bounds()
        
        # Yatay çarpışma
        if self.velocity_x > 0:
            self.x = x2 - w1
        elif self.velocity_x < 0:
            self.x = x2 + w2
            
        # Dikey çarpışma
        if self.velocity_y > 0:
            self.y = y2 - h1
        elif self.velocity_y < 0:
            self.y = y2 + h2
            
        # Hızı sıfırla
        self.stop() 