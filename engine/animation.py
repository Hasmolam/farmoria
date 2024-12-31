import pygame
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import json

@dataclass
class Bone:
    """Kemik sınıfı"""
    name: str
    parent: Optional['Bone']
    length: float
    angle: float  # Radyan cinsinden
    scale: Tuple[float, float] = (1.0, 1.0)
    position: Tuple[float, float] = (0.0, 0.0)
    children: List['Bone'] = None
    sprite: Optional[pygame.Surface] = None
    sprite_offset: Tuple[float, float] = (0.0, 0.0)
    flip_x: bool = False
    flip_y: bool = False
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.parent:
            self.parent.add_child(self)
    
    def add_child(self, bone: 'Bone'):
        """Alt kemik ekle"""
        self.children.append(bone)
    
    def get_world_matrix(self) -> np.ndarray:
        """Dünya dönüşüm matrisini hesapla"""
        # Temel dönüşüm matrisi
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        # Ölçekleme matrisi
        scale_matrix = np.array([
            [self.scale[0], 0, 0],
            [0, self.scale[1], 0],
            [0, 0, 1]
        ])
        
        # Rotasyon matrisi
        rotation_matrix = np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])
        
        # Öteleme matrisi
        translation_matrix = np.array([
            [1, 0, self.position[0]],
            [0, 1, self.position[1]],
            [0, 0, 1]
        ])
        
        # Matrisleri birleştir
        local_matrix = translation_matrix @ rotation_matrix @ scale_matrix
        
        # Üst kemiklerin matrislerini ekle
        if self.parent:
            return self.parent.get_world_matrix() @ local_matrix
        return local_matrix
    
    def get_tip_position(self) -> Tuple[float, float]:
        """Kemiğin uç noktasının pozisyonunu hesapla"""
        world_matrix = self.get_world_matrix()
        tip = np.array([self.length, 0, 1])
        transformed_tip = world_matrix @ tip
        return (transformed_tip[0], transformed_tip[1])
    
    def set_sprite(self, sprite: pygame.Surface, offset: Tuple[float, float] = (0.0, 0.0)):
        """Kemiğe sprite ata"""
        self.sprite = sprite
        self.sprite_offset = offset
    
    def flip_sprite(self, flip_x: bool = False, flip_y: bool = False):
        """Sprite'ı çevir"""
        self.flip_x = flip_x
        self.flip_y = flip_y

@dataclass
class Keyframe:
    """Animasyon karesi"""
    time: float  # Saniye cinsinden
    bone_poses: Dict[str, Tuple[float, float, float]]  # Kemik adı -> (pozisyon_x, pozisyon_y, açı)

class Animation:
    """Kemik animasyonu"""
    def __init__(self, name: str, duration: float):
        self.name = name
        self.duration = duration
        self.keyframes: List[Keyframe] = []
        self.current_time = 0.0
        self.is_playing = False
        self.is_looping = True
    
    def add_keyframe(self, time: float, bone_poses: Dict[str, Tuple[float, float, float]]):
        """Yeni bir animasyon karesi ekle"""
        keyframe = Keyframe(time, bone_poses)
        # Zamanı sırala
        insert_index = 0
        for i, kf in enumerate(self.keyframes):
            if kf.time > time:
                break
            insert_index = i + 1
        self.keyframes.insert(insert_index, keyframe)
    
    def get_pose_at_time(self, time: float) -> Dict[str, Tuple[float, float, float]]:
        """Belirli bir zamandaki pozu hesapla"""
        if not self.keyframes:
            return {}
        
        # Zaman sınırlarını kontrol et
        if time <= self.keyframes[0].time:
            return self.keyframes[0].bone_poses
        if time >= self.keyframes[-1].time:
            return self.keyframes[-1].bone_poses
        
        # İki kare arasında interpolasyon yap
        for i in range(len(self.keyframes) - 1):
            frame1 = self.keyframes[i]
            frame2 = self.keyframes[i + 1]
            
            if frame1.time <= time <= frame2.time:
                # İki kare arasındaki t değerini hesapla (0-1 arası)
                t = (time - frame1.time) / (frame2.time - frame1.time)
                
                # Doğrusal interpolasyon
                result = {}
                for bone_name in frame1.bone_poses:
                    if bone_name in frame2.bone_poses:
                        pos1_x, pos1_y, angle1 = frame1.bone_poses[bone_name]
                        pos2_x, pos2_y, angle2 = frame2.bone_poses[bone_name]
                        
                        # Açı interpolasyonu için en kısa yolu seç
                        angle_diff = angle2 - angle1
                        if angle_diff > math.pi:
                            angle_diff -= 2 * math.pi
                        elif angle_diff < -math.pi:
                            angle_diff += 2 * math.pi
                        
                        result[bone_name] = (
                            pos1_x + (pos2_x - pos1_x) * t,
                            pos1_y + (pos2_y - pos1_y) * t,
                            angle1 + angle_diff * t
                        )
                return result
        
        return self.keyframes[-1].bone_poses
    
    def update(self, dt: float):
        """Animasyonu güncelle"""
        if not self.is_playing:
            return
        
        self.current_time += dt
        
        if self.current_time >= self.duration:
            if self.is_looping:
                self.current_time %= self.duration
            else:
                self.current_time = self.duration
                self.is_playing = False
    
    def play(self, loop: bool = True):
        """Animasyonu başlat"""
        self.is_playing = True
        self.is_looping = loop
        self.current_time = 0.0
    
    def stop(self):
        """Animasyonu durdur"""
        self.is_playing = False
        self.current_time = 0.0
    
    def pause(self):
        """Animasyonu duraklat"""
        self.is_playing = False

class Skeleton:
    """İskelet sistemi"""
    def __init__(self):
        self.bones: Dict[str, Bone] = {}
        self.root_bones: List[Bone] = []
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.sprite_sheet: Optional[pygame.Surface] = None
        self.sprite_regions: Dict[str, pygame.Rect] = {}
    
    def add_bone(self, name: str, length: float, parent_name: Optional[str] = None,
                angle: float = 0.0, position: Tuple[float, float] = (0.0, 0.0)):
        """Yeni bir kemik ekle"""
        parent = self.bones.get(parent_name) if parent_name else None
        bone = Bone(name, parent, length, angle, position=position)
        self.bones[name] = bone
        
        if not parent:
            self.root_bones.append(bone)
    
    def add_animation(self, animation: Animation):
        """Yeni bir animasyon ekle"""
        self.animations[animation.name] = animation
    
    def play_animation(self, name: str, loop: bool = True):
        """Animasyonu oynat"""
        if name in self.animations:
            self.current_animation = self.animations[name]
            self.current_animation.play(loop)
    
    def update(self, dt: float):
        """İskeleti güncelle"""
        if self.current_animation and self.current_animation.is_playing:
            self.current_animation.update(dt)
            
            # Güncel pozu uygula
            current_pose = self.current_animation.get_pose_at_time(
                self.current_animation.current_time
            )
            
            for bone_name, (pos_x, pos_y, angle) in current_pose.items():
                if bone_name in self.bones:
                    bone = self.bones[bone_name]
                    bone.position = (pos_x, pos_y)
                    bone.angle = angle
    
    def draw(self, surface: pygame.Surface, position: Tuple[float, float], 
             debug: bool = False, color: Tuple[int, int, int] = (255, 0, 0)):
        """İskeleti çiz"""
        for bone in self.root_bones:
            self._draw_bone_recursive(surface, bone, position, debug, color)
    
    def _draw_bone_recursive(self, surface: pygame.Surface, bone: Bone,
                           offset: Tuple[float, float], debug: bool,
                           color: Tuple[int, int, int]):
        """Kemiği ve alt kemiklerini çiz"""
        start_pos = bone.position
        tip_pos = bone.get_tip_position()
        
        # Sprite'ı çiz
        if bone.sprite:
            # Sprite'ı döndür ve ölçekle
            rotated_sprite = pygame.transform.rotate(
                pygame.transform.flip(bone.sprite, bone.flip_x, bone.flip_y),
                -math.degrees(bone.angle)  # Pygame açıları saat yönünün tersine
            )
            
            # Sprite pozisyonunu hesapla
            sprite_rect = rotated_sprite.get_rect()
            sprite_x = offset[0] + start_pos[0] + bone.sprite_offset[0]
            sprite_y = offset[1] + start_pos[1] + bone.sprite_offset[1]
            sprite_rect.center = (sprite_x, sprite_y)
            
            # Sprite'ı çiz
            surface.blit(rotated_sprite, sprite_rect)
        
        if debug:
            # Debug modunda kemikleri çizgilerle göster
            pygame.draw.line(
                surface,
                color,
                (offset[0] + start_pos[0], offset[1] + start_pos[1]),
                (offset[0] + tip_pos[0], offset[1] + tip_pos[1]),
                2
            )
            
            # Eklem noktalarını göster
            pygame.draw.circle(
                surface,
                (0, 255, 0),
                (int(offset[0] + start_pos[0]), int(offset[1] + start_pos[1])),
                4
            )
        
        # Alt kemikleri çiz
        for child in bone.children:
            self._draw_bone_recursive(surface, child, offset, debug, color)
    
    def save_to_file(self, filename: str):
        """İskelet ve animasyonları dosyaya kaydet"""
        data = {
            'bones': {},
            'animations': {},
            'sprite_regions': {}
        }
        
        # Kemik verilerini kaydet
        for name, bone in self.bones.items():
            data['bones'][name] = {
                'length': bone.length,
                'parent': bone.parent.name if bone.parent else None,
                'angle': bone.angle,
                'position': bone.position,
                'scale': bone.scale,
                'sprite_offset': bone.sprite_offset,
                'flip_x': bone.flip_x,
                'flip_y': bone.flip_y
            }
        
        # Animasyon verilerini kaydet
        for name, animation in self.animations.items():
            data['animations'][name] = {
                'duration': animation.duration,
                'keyframes': [
                    {
                        'time': kf.time,
                        'bone_poses': kf.bone_poses
                    }
                    for kf in animation.keyframes
                ]
            }
        
        # Sprite bölgelerini kaydet
        if self.sprite_regions:
            data['sprite_regions'] = {
                name: (rect.x, rect.y, rect.width, rect.height)
                for name, rect in self.sprite_regions.items()
            }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str, sprite_sheet: Optional[pygame.Surface] = None) -> 'Skeleton':
        """İskelet ve animasyonları dosyadan yükle"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        skeleton = cls()
        
        # Sprite sheet'i yükle
        if sprite_sheet and 'sprite_regions' in data:
            skeleton.load_sprite_sheet(sprite_sheet, {
                name: tuple(rect)
                for name, rect in data['sprite_regions'].items()
            })
        
        # Önce köksüz kemikleri yükle
        for name, bone_data in data['bones'].items():
            if not bone_data['parent']:
                skeleton.add_bone(
                    name,
                    bone_data['length'],
                    angle=bone_data['angle'],
                    position=tuple(bone_data['position'])
                )
                # Sprite özelliklerini ayarla
                bone = skeleton.bones[name]
                bone.sprite_offset = tuple(bone_data.get('sprite_offset', (0.0, 0.0)))
                bone.flip_x = bone_data.get('flip_x', False)
                bone.flip_y = bone_data.get('flip_y', False)
        
        # Sonra alt kemikleri yükle
        for name, bone_data in data['bones'].items():
            if bone_data['parent']:
                skeleton.add_bone(
                    name,
                    bone_data['length'],
                    parent_name=bone_data['parent'],
                    angle=bone_data['angle'],
                    position=tuple(bone_data['position'])
                )
                # Sprite özelliklerini ayarla
                bone = skeleton.bones[name]
                bone.sprite_offset = tuple(bone_data.get('sprite_offset', (0.0, 0.0)))
                bone.flip_x = bone_data.get('flip_x', False)
                bone.flip_y = bone_data.get('flip_y', False)
        
        # Animasyonları yükle
        for name, anim_data in data['animations'].items():
            animation = Animation(name, anim_data['duration'])
            
            for kf_data in anim_data['keyframes']:
                animation.add_keyframe(
                    kf_data['time'],
                    {k: tuple(v) for k, v in kf_data['bone_poses'].items()}
                )
            
            skeleton.add_animation(animation)
        
        return skeleton
    
    def load_sprite_sheet(self, sprite_sheet: pygame.Surface, regions: Dict[str, Tuple[int, int, int, int]]):
        """Sprite sheet'i yükle ve bölgeleri tanımla"""
        self.sprite_sheet = sprite_sheet
        self.sprite_regions = {
            name: pygame.Rect(*rect)
            for name, rect in regions.items()
        }
    
    def set_bone_sprite(self, bone_name: str, sprite_name: str, 
                       offset: Tuple[float, float] = (0.0, 0.0)):
        """Kemiğe sprite ata"""
        if bone_name in self.bones and sprite_name in self.sprite_regions:
            bone = self.bones[bone_name]
            region = self.sprite_regions[sprite_name]
            sprite = pygame.Surface(region.size, pygame.SRCALPHA)
            sprite.blit(self.sprite_sheet, (0, 0), region)
            bone.set_sprite(sprite, offset) 