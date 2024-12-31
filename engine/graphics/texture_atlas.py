import pygame
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class TextureRegion:
    """Texture atlas içindeki bir bölgeyi temsil eder"""
    x: int
    y: int
    width: int
    height: int
    name: str

class TextureAtlas:
    """Birden fazla sprite'ı tek bir texturede yöneten sistem"""
    def __init__(self, texture_size: Tuple[int, int] = (1024, 1024)):
        self.texture_size = texture_size
        self.surface = pygame.Surface(texture_size, pygame.SRCALPHA)
        self.regions: Dict[str, TextureRegion] = {}
        self.next_x = 0
        self.next_y = 0
        self.row_height = 0
    
    def add_texture(self, name: str, surface: pygame.Surface) -> Optional[TextureRegion]:
        """Yeni bir texture ekle"""
        width, height = surface.get_size()
        
        # Yeni satıra geçme kontrolü
        if self.next_x + width > self.texture_size[0]:
            self.next_x = 0
            self.next_y += self.row_height
            self.row_height = 0
        
        # Yükseklik kontrolü
        if self.next_y + height > self.texture_size[1]:
            return None  # Atlas dolu
        
        # Texture'ı kopyala
        self.surface.blit(surface, (self.next_x, self.next_y))
        
        # Bölgeyi kaydet
        region = TextureRegion(
            x=self.next_x,
            y=self.next_y,
            width=width,
            height=height,
            name=name
        )
        self.regions[name] = region
        
        # Sonraki pozisyonu güncelle
        self.next_x += width
        self.row_height = max(self.row_height, height)
        
        return region
    
    def get_region(self, name: str) -> Optional[TextureRegion]:
        """İsme göre texture bölgesini getir"""
        return self.regions.get(name)
    
    def get_texture(self, name: str) -> Optional[pygame.Surface]:
        """İsme göre texture'ı getir"""
        region = self.get_region(name)
        if region:
            return self.surface.subsurface(pygame.Rect(
                region.x, region.y, region.width, region.height
            ))
        return None
    
    def save(self, atlas_path: str, metadata_path: str):
        """Atlas'ı ve metadata'yı kaydet"""
        # Atlas texture'ını kaydet
        pygame.image.save(self.surface, atlas_path)
        
        # Metadata'yı kaydet
        metadata = {
            'size': self.texture_size,
            'regions': {
                name: {
                    'x': region.x,
                    'y': region.y,
                    'width': region.width,
                    'height': region.height,
                    'name': region.name
                }
                for name, region in self.regions.items()
            }
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    @classmethod
    def load(cls, atlas_path: str, metadata_path: str) -> 'TextureAtlas':
        """Atlas'ı ve metadata'yı yükle"""
        # Metadata'yı yükle
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Atlas'ı oluştur
        atlas = cls(tuple(metadata['size']))
        
        # Atlas texture'ını yükle
        atlas.surface = pygame.image.load(atlas_path).convert_alpha()
        
        # Bölgeleri yükle
        for name, region_data in metadata['regions'].items():
            atlas.regions[name] = TextureRegion(**region_data)
        
        return atlas

class TextureManager:
    """Texture atlaslarını yöneten sistem"""
    def __init__(self):
        self.atlases: Dict[str, TextureAtlas] = {}
    
    def create_atlas(self, name: str, size: Tuple[int, int] = (1024, 1024)) -> TextureAtlas:
        """Yeni bir atlas oluştur"""
        atlas = TextureAtlas(size)
        self.atlases[name] = atlas
        return atlas
    
    def get_atlas(self, name: str) -> Optional[TextureAtlas]:
        """İsme göre atlas'ı getir"""
        return self.atlases.get(name)
    
    def load_directory(self, directory: str, atlas_name: str) -> TextureAtlas:
        """Bir dizindeki tüm texture'ları yükle ve atlas oluştur"""
        atlas = self.create_atlas(atlas_name)
        
        # Dizindeki tüm .png dosyalarını tara
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                path = os.path.join(directory, filename)
                name = os.path.splitext(filename)[0]
                
                # Texture'ı yükle ve atlas'a ekle
                surface = pygame.image.load(path).convert_alpha()
                atlas.add_texture(name, surface)
        
        return atlas
    
    def save_atlas(self, name: str, directory: str):
        """Atlas'ı ve metadata'yı kaydet"""
        atlas = self.get_atlas(name)
        if atlas:
            atlas_path = os.path.join(directory, f"{name}.png")
            metadata_path = os.path.join(directory, f"{name}.json")
            atlas.save(atlas_path, metadata_path)
    
    def load_atlas(self, name: str, directory: str):
        """Atlas'ı ve metadata'yı yükle"""
        atlas_path = os.path.join(directory, f"{name}.png")
        metadata_path = os.path.join(directory, f"{name}.json")
        
        atlas = TextureAtlas.load(atlas_path, metadata_path)
        self.atlases[name] = atlas 