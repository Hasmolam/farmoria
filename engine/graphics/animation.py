import pygame
from typing import Dict, List, Optional, Tuple
import json
import math
from dataclasses import dataclass
from ..core.base import GameObject
from . import DebugCategory, DebugLevel, debug_manager

@dataclass
class Bone:
    """İskelet animasyonu için kemik sınıfı"""
    name: str
    parent: Optional[str]
    x: float
    y: float
    rotation: float
    scale_x: float = 1.0
    scale_y: float = 1.0
    
    def to_dict(self) -> dict:
        """Kemiği sözlüğe dönüştürür"""
        return {
            'name': self.name,
            'parent': self.parent,
            'x': self.x,
            'y': self.y,
            'rotation': self.rotation,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Bone':
        """Sözlükten kemik oluşturur"""
        return cls(
            name=data['name'],
            parent=data['parent'],
            x=data['x'],
            y=data['y'],
            rotation=data['rotation'],
            scale_x=data.get('scale_x', 1.0),
            scale_y=data.get('scale_y', 1.0)
        )

@dataclass
class Keyframe:
    """Animasyon için anahtar kare sınıfı"""
    time: float
    bone_name: str
    x: float
    y: float
    rotation: float
    scale_x: float = 1.0
    scale_y: float = 1.0
    
    def to_dict(self) -> dict:
        """Anahtar kareyi sözlüğe dönüştürür"""
        return {
            'time': self.time,
            'bone_name': self.bone_name,
            'x': self.x,
            'y': self.y,
            'rotation': self.rotation,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Keyframe':
        """Sözlükten anahtar kare oluşturur"""
        return cls(
            time=data['time'],
            bone_name=data['bone_name'],
            x=data['x'],
            y=data['y'],
            rotation=data['rotation'],
            scale_x=data.get('scale_x', 1.0),
            scale_y=data.get('scale_y', 1.0)
        )

class Animation:
    """İskelet animasyonu sınıfı"""
    def __init__(self, name: str, duration: float = 1.0, loop: bool = True):
        self.name = name
        self.duration = duration
        self.loop = loop
        self.keyframes: List[Keyframe] = []
        
    def add_keyframe(self, keyframe: Keyframe):
        """Anahtar kare ekler"""
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time)  # Zamana göre sırala
        
    def get_keyframes_for_bone(self, bone_name: str) -> List[Keyframe]:
        """Belirli bir kemik için anahtar kareleri döndürür"""
        return [k for k in self.keyframes if k.bone_name == bone_name]
        
    def to_dict(self) -> dict:
        """Animasyonu sözlüğe dönüştürür"""
        return {
            'name': self.name,
            'duration': self.duration,
            'loop': self.loop,
            'keyframes': [k.to_dict() for k in self.keyframes]
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Animation':
        """Sözlükten animasyon oluşturur"""
        animation = cls(
            name=data['name'],
            duration=data['duration'],
            loop=data['loop']
        )
        for keyframe_data in data['keyframes']:
            animation.add_keyframe(Keyframe.from_dict(keyframe_data))
        return animation

class Skeleton(GameObject):
    """İskelet sınıfı"""
    def __init__(self, name: str = "Skeleton"):
        super().__init__(name)
        self.bones: Dict[str, Bone] = {}
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
        self.animation_time = 0.0
        self.sprite_surface: Optional[pygame.Surface] = None
        self.sprite_offset = (0, 0)
        
    def add_bone(self, bone: Bone):
        """Kemik ekler"""
        self.bones[bone.name] = bone
        
    def get_bone(self, name: str) -> Optional[Bone]:
        """İsme göre kemik döndürür"""
        return self.bones.get(name)
        
    def add_animation(self, animation: Animation):
        """Animasyon ekler"""
        self.animations[animation.name] = animation
        
    def get_animation(self, name: str) -> Optional[Animation]:
        """İsme göre animasyon döndürür"""
        return self.animations.get(name)
        
    def play_animation(self, name: str):
        """Animasyon oynatır"""
        if name in self.animations:
            self.current_animation = name
            self.animation_time = 0.0
            debug_manager.log(f"Playing animation: {name}", DebugCategory.GRAPHICS)
            
    def stop_animation(self):
        """Animasyonu durdurur"""
        self.current_animation = None
        self.animation_time = 0.0
        
    def set_sprite(self, surface: pygame.Surface, offset: Tuple[int, int] = (0, 0)):
        """Sprite'ı ayarlar"""
        self.sprite_surface = surface
        self.sprite_offset = offset
        
    def update(self, dt: float):
        """İskeleti günceller"""
        super().update(dt)
        
        if not self.current_animation:
            return
            
        animation = self.animations[self.current_animation]
        self.animation_time += dt
        
        # Döngü kontrolü
        if self.animation_time > animation.duration:
            if animation.loop:
                self.animation_time %= animation.duration
            else:
                self.stop_animation()
                return
                
        # Her kemik için interpolasyon yap
        for bone_name, bone in self.bones.items():
            keyframes = animation.get_keyframes_for_bone(bone_name)
            if not keyframes:
                continue
                
            # Önceki ve sonraki anahtar kareleri bul
            prev_keyframe = None
            next_keyframe = None
            for keyframe in keyframes:
                if keyframe.time <= self.animation_time:
                    prev_keyframe = keyframe
                else:
                    next_keyframe = keyframe
                    break
                    
            if prev_keyframe and next_keyframe:
                # İki anahtar kare arasında interpolasyon yap
                t = (self.animation_time - prev_keyframe.time) / (next_keyframe.time - prev_keyframe.time)
                bone.x = self._lerp(prev_keyframe.x, next_keyframe.x, t)
                bone.y = self._lerp(prev_keyframe.y, next_keyframe.y, t)
                bone.rotation = self._lerp_angle(prev_keyframe.rotation, next_keyframe.rotation, t)
                bone.scale_x = self._lerp(prev_keyframe.scale_x, next_keyframe.scale_x, t)
                bone.scale_y = self._lerp(prev_keyframe.scale_y, next_keyframe.scale_y, t)
            elif prev_keyframe:
                # Son anahtar kareyi kullan
                bone.x = prev_keyframe.x
                bone.y = prev_keyframe.y
                bone.rotation = prev_keyframe.rotation
                bone.scale_x = prev_keyframe.scale_x
                bone.scale_y = prev_keyframe.scale_y
                
    def draw(self, surface: pygame.Surface):
        """İskeleti çizer"""
        if not self.enabled or not self.sprite_surface:
            return
            
        # Her kemiği çiz
        for bone_name, bone in self.bones.items():
            # Kemik transformasyonunu hesapla
            transform = pygame.Surface(self.sprite_surface.get_size(), pygame.SRCALPHA)
            
            # Sprite'ı kopyala
            transform.blit(self.sprite_surface, (0, 0))
            
            # Dönüşümleri uygula
            rotated = pygame.transform.rotate(transform, -bone.rotation)
            scaled = pygame.transform.scale(rotated,
                (int(rotated.get_width() * bone.scale_x),
                 int(rotated.get_height() * bone.scale_y)))
            
            # Pozisyonu hesapla
            x = bone.x - scaled.get_width() / 2 + self.sprite_offset[0]
            y = bone.y - scaled.get_height() / 2 + self.sprite_offset[1]
            
            # Çiz
            surface.blit(scaled, (x, y))
            
    def save(self, file_path: str):
        """İskeleti dosyaya kaydeder"""
        data = {
            'bones': {name: bone.to_dict() for name, bone in self.bones.items()},
            'animations': {name: anim.to_dict() for name, anim in self.animations.items()}
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def load(cls, file_path: str) -> 'Skeleton':
        """Dosyadan iskelet yükler"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        skeleton = cls()
        
        # Kemikleri yükle
        for bone_data in data['bones'].values():
            skeleton.add_bone(Bone.from_dict(bone_data))
            
        # Animasyonları yükle
        for animation_data in data['animations'].values():
            skeleton.add_animation(Animation.from_dict(animation_data))
            
        return skeleton
        
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Doğrusal interpolasyon"""
        return a + (b - a) * t
        
    def _lerp_angle(self, a: float, b: float, t: float) -> float:
        """Açı interpolasyonu"""
        diff = (b - a + 180) % 360 - 180
        return a + diff * t 

class Animation:
    """Sprite animasyonu sınıfı"""
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1, loop: bool = True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.time_elapsed = 0.0
        self.finished = False
        
    def update(self, dt: float):
        """Animasyonu günceller"""
        if self.finished and not self.loop:
            return
            
        self.time_elapsed += dt
        if self.time_elapsed >= self.frame_duration:
            self.time_elapsed = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    
    def get_current_frame(self) -> pygame.Surface:
        """Mevcut frame'i döndürür"""
        return self.frames[self.current_frame]
        
    def reset(self):
        """Animasyonu sıfırlar"""
        self.current_frame = 0
        self.time_elapsed = 0.0
        self.finished = False
        
    def is_finished(self) -> bool:
        """Animasyonun bitip bitmediğini döndürür"""
        return self.finished

class AnimationManager:
    """Animasyon yönetim sınıfı"""
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
        
    def add_animation(self, name: str, animation: Animation):
        """Yeni animasyon ekler"""
        self.animations[name] = animation
        if self.current_animation is None:
            self.current_animation = name
            
    def play(self, name: str):
        """Belirtilen animasyonu oynatır"""
        if name in self.animations:
            if self.current_animation != name:
                self.animations[name].reset()
                self.current_animation = name
                
    def update(self, dt: float):
        """Mevcut animasyonu günceller"""
        if self.current_animation:
            self.animations[self.current_animation].update(dt)
            
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Mevcut frame'i döndürür"""
        if self.current_animation:
            return self.animations[self.current_animation].get_current_frame()
        return None
        
    def is_playing(self, name: str) -> bool:
        """Belirtilen animasyonun oynatılıp oynatılmadığını döndürür"""
        return self.current_animation == name
        
    def get_current_animation(self) -> Optional[str]:
        """Mevcut animasyon adını döndürür"""
        return self.current_animation
        
    def reset_current(self):
        """Mevcut animasyonu sıfırlar"""
        if self.current_animation:
            self.animations[self.current_animation].reset()
            
    def clear(self):
        """Tüm animasyonları temizler"""
        self.animations.clear()
        self.current_animation = None

# Sprite sheet'ten animasyon oluşturma yardımcı fonksiyonları
def load_spritesheet(filename: str, frame_width: int, frame_height: int) -> List[pygame.Surface]:
    """Sprite sheet'i yükler ve frame'lere böler"""
    spritesheet = pygame.image.load(filename)
    frames = []
    
    sheet_width = spritesheet.get_width()
    sheet_height = spritesheet.get_height()
    
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(spritesheet, (0, 0), (x, y, frame_width, frame_height))
            frames.append(frame)
            
    return frames
    
def create_animation_from_spritesheet(filename: str, frame_width: int, frame_height: int,
                                    frame_duration: float = 0.1, loop: bool = True) -> Animation:
    """Sprite sheet'ten animasyon oluşturur"""
    frames = load_spritesheet(filename, frame_width, frame_height)
    return Animation(frames, frame_duration, loop)
    
def load_animation_config(config_file: str) -> Dict[str, Animation]:
    """JSON config dosyasından animasyonları yükler"""
    animations = {}
    
    with open(config_file, 'r') as f:
        config = json.load(f)
        
    for anim_name, anim_data in config['animations'].items():
        spritesheet = anim_data['spritesheet']
        frame_width = anim_data['frame_width']
        frame_height = anim_data['frame_height']
        frame_duration = anim_data.get('frame_duration', 0.1)
        loop = anim_data.get('loop', True)
        
        animation = create_animation_from_spritesheet(
            spritesheet, frame_width, frame_height, frame_duration, loop
        )
        animations[anim_name] = animation
        
    return animations 