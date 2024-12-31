import pygame
import math
from typing import Dict, Tuple
from .core import GameObject, GameSystem
from .sprite_generator import SpriteGenerator

class Player(GameObject):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = 0.1
        self.z_index = 1000  # Her zaman karoların üstünde çizilsin
        
        # Sprite özellikleri
        self.sprite_width = 64
        self.sprite_height = 96
        self.base_color = (50, 120, 190)
        self.detail_color = (255, 255, 255)
        
        # Sprite'ları oluştur
        self.sprites = SpriteGenerator.create_directional_sprites(
            self.sprite_width,
            self.sprite_height,
            self.base_color,
            self.detail_color
        )
        self.current_direction = 'down'
        
        # Animasyon özellikleri
        self.animation_time = 0
        self.is_moving = False
        self.bob_height = 4
        self.bob_speed = 8
        self.sway_amount = 2
        
    def move(self, dx: float, dy: float) -> None:
        self.is_moving = dx != 0 or dy != 0
        
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        if abs(dx) > abs(dy):
            if dx > 0:
                self.current_direction = 'right'
            elif dx < 0:
                self.current_direction = 'left'
        else:
            if dy > 0:
                self.current_direction = 'down'
            elif dy < 0:
                self.current_direction = 'up'
                
    def update(self, dt: float) -> None:
        if self.is_moving:
            self.animation_time += dt
        else:
            self.animation_time = 0
            
    def get_animation_offset(self) -> Tuple[float, float]:
        if not self.is_moving:
            return 0, 0
            
        bob_offset = math.sin(self.animation_time * self.bob_speed) * self.bob_height
        sway_offset = math.cos(self.animation_time * self.bob_speed) * self.sway_amount
        
        return sway_offset, bob_offset
        
    def draw(self, screen: pygame.Surface) -> None:
        # İzometrik koordinatları hesapla (harita sisteminden alınacak)
        iso_map = self.engine.get_system("isometric_map")
        if not iso_map:
            return
            
        iso_x, iso_y = iso_map.cart_to_iso(self.x, self.y)
        
        # Ekran merkezleme
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 4
        
        # Animasyon offsetlerini al
        sway_offset, bob_offset = self.get_animation_offset()
        
        # Sprite'ı çiz
        sprite = self.sprites[self.current_direction]
        sprite_rect = sprite.get_rect()
        sprite_rect.centerx = int(screen_center_x + iso_x + sway_offset)
        sprite_rect.bottom = int(screen_center_y + iso_y - bob_offset)
        
        screen.blit(sprite, sprite_rect)
        
    def serialize(self) -> Dict:
        data = super().serialize()
        data.update({
            'x': self.x,
            'y': self.y,
            'current_direction': self.current_direction
        })
        return data
        
    def deserialize(self, data: Dict) -> None:
        super().deserialize(data)
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.current_direction = data.get('current_direction', 'down')

class PlayerController(GameSystem):
    def __init__(self, player: Player):
        super().__init__("player_controller")
        self.player = player
        
    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
            
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        self.player.move(dx, dy)
        
        # Harita sınırlarını kontrol et
        iso_map = self.engine.get_system("isometric_map")
        if iso_map:
            self.player.x = max(0, min(self.player.x, iso_map.width - 1))
            self.player.y = max(0, min(self.player.y, iso_map.height - 1))
            
    def serialize(self) -> Dict:
        return {}  # Kontrolcünün kaydetmesi gereken bir durum yok
        
    def deserialize(self, data: Dict) -> None:
        pass  # Kontrolcünün yüklemesi gereken bir durum yok 