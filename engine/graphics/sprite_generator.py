import pygame
import math
from .animation import Animation, AnimationManager

class SpriteGenerator:
    @staticmethod
    def create_character_sprite(width: int, height: int, base_color: tuple, detail_color: tuple, direction: str = 'up') -> pygame.Surface:
        # Temel karakter sprite'ı oluştur
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Vücut (oval şekil)
        body_height = int(height * 0.6)
        body_rect = pygame.Rect(
            width//4,
            height - body_height,
            width//2,
            body_height
        )
        pygame.draw.ellipse(surface, base_color, body_rect)
        
        # Baş (daire)
        head_size = int(width * 0.4)
        head_y = height - body_height if direction == 'up' else height - body_height * 0.7
        head_pos = (width//2, head_y)
        pygame.draw.circle(surface, base_color, head_pos, head_size)
        
        # Gözler
        eye_size = int(head_size * 0.2)
        eye_offset_y = -eye_size if direction == 'up' else eye_size
        left_eye_pos = (head_pos[0] - eye_size*2, head_pos[1] + eye_offset_y)
        right_eye_pos = (head_pos[0] + eye_size*2, head_pos[1] + eye_offset_y)
        pygame.draw.circle(surface, detail_color, left_eye_pos, eye_size)
        pygame.draw.circle(surface, detail_color, right_eye_pos, eye_size)
        
        return surface
    
    @staticmethod
    def create_directional_sprites(width: int, height: int, base_color: tuple, detail_color: tuple) -> dict:
        # Dört yön için sprite'lar oluştur
        sprites = {}
        
        # Yukarı bakan sprite
        sprites['up'] = SpriteGenerator.create_character_sprite(width, height, base_color, detail_color, 'up')
        
        # Aşağı bakan sprite (farklı göz pozisyonuyla)
        sprites['down'] = SpriteGenerator.create_character_sprite(width, height, base_color, detail_color, 'down')
        
        # Sağa bakan sprite
        sprites['right'] = pygame.transform.rotate(sprites['up'], -30)
        
        # Sola bakan sprite
        sprites['left'] = pygame.transform.flip(sprites['right'], True, False)
        
        return sprites 
    
    @staticmethod
    def create_walking_animation(sprite: pygame.Surface, frames: int = 6) -> Animation:
        """Yürüme animasyonu oluşturur"""
        animation_frames = []
        
        for i in range(frames):
            # Her frame için sprite'ı hafifçe değiştir
            frame = sprite.copy()
            offset = math.sin(i * (2 * math.pi / frames)) * 2
            frame_rect = frame.get_rect()
            
            # Frame'i yukarı aşağı hareket ettir
            new_frame = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
            new_frame.blit(frame, (0, offset))
            animation_frames.append(new_frame)
        
        return Animation(animation_frames, frame_duration=0.1)
    
    @staticmethod
    def create_character_animations(width: int, height: int, base_color: tuple, detail_color: tuple) -> AnimationManager:
        """Karakter için tüm animasyonları oluşturur"""
        manager = AnimationManager()
        
        # Temel sprite'ları oluştur
        directional_sprites = SpriteGenerator.create_directional_sprites(width, height, base_color, detail_color)
        
        # Her yön için yürüme animasyonları oluştur
        for direction, sprite in directional_sprites.items():
            walk_anim = SpriteGenerator.create_walking_animation(sprite)
            manager.add_animation(f"walk_{direction}", walk_anim)
        
        return manager 