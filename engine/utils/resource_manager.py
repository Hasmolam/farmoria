"""
Kaynak yönetim sistemi.
Oyun içi varlıkların (texture, ses, font vb.) yüklenmesi ve yönetimini sağlar.
"""

import os
import pygame
from typing import Dict, Optional, Any
from ..core.base import GameSystem

class ResourceManager(GameSystem):
    """Kaynak yönetim sistemi"""
    
    def __init__(self):
        super().__init__("ResourceManager")
        self._textures: Dict[str, pygame.Surface] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._base_path = "assets"
        
    def set_base_path(self, path: str):
        """Temel kaynak dizinini ayarlar"""
        self._base_path = path
        
    def get_full_path(self, relative_path: str) -> str:
        """Tam dosya yolunu döndürür"""
        return os.path.join(self._base_path, relative_path)
        
    # Texture yönetimi
    def load_texture(self, name: str, file_path: str) -> Optional[pygame.Surface]:
        """Texture yükler"""
        try:
            full_path = self.get_full_path(file_path)
            texture = pygame.image.load(full_path).convert_alpha()
            self._textures[name] = texture
            return texture
        except Exception as e:
            print(f"Texture yüklenirken hata: {e}")
            return None
            
    def get_texture(self, name: str) -> Optional[pygame.Surface]:
        """İsme göre texture döndürür"""
        return self._textures.get(name)
        
    def remove_texture(self, name: str):
        """Texture'ı kaldırır"""
        if name in self._textures:
            del self._textures[name]
            
    # Ses yönetimi
    def load_sound(self, name: str, file_path: str) -> Optional[pygame.mixer.Sound]:
        """Ses dosyası yükler"""
        try:
            full_path = self.get_full_path(file_path)
            sound = pygame.mixer.Sound(full_path)
            self._sounds[name] = sound
            return sound
        except Exception as e:
            print(f"Ses yüklenirken hata: {e}")
            return None
            
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """İsme göre ses dosyası döndürür"""
        return self._sounds.get(name)
        
    def remove_sound(self, name: str):
        """Ses dosyasını kaldırır"""
        if name in self._sounds:
            self._sounds[name].stop()
            del self._sounds[name]
            
    # Font yönetimi
    def load_font(self, name: str, file_path: str, size: int) -> Optional[pygame.font.Font]:
        """Font yükler"""
        try:
            full_path = self.get_full_path(file_path)
            font = pygame.font.Font(full_path, size)
            self._fonts[name] = font
            return font
        except Exception as e:
            print(f"Font yüklenirken hata: {e}")
            return None
            
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """İsme göre font döndürür"""
        return self._fonts.get(name)
        
    def remove_font(self, name: str):
        """Font'u kaldırır"""
        if name in self._fonts:
            del self._fonts[name]
            
    # Genel yönetim
    def clear(self):
        """Tüm kaynakları temizler"""
        self._textures.clear()
        for sound in self._sounds.values():
            sound.stop()
        self._sounds.clear()
        self._fonts.clear()
        
    def preload_resources(self, resource_list: Dict[str, Dict[str, Any]]):
        """Birden fazla kaynağı önceden yükler
        
        resource_list formatı:
        {
            "textures": {"name": "file_path", ...},
            "sounds": {"name": "file_path", ...},
            "fonts": {"name": {"path": "file_path", "size": size}, ...}
        }
        """
        # Texture'ları yükle
        for name, path in resource_list.get("textures", {}).items():
            self.load_texture(name, path)
            
        # Sesleri yükle
        for name, path in resource_list.get("sounds", {}).items():
            self.load_sound(name, path)
            
        # Fontları yükle
        for name, font_info in resource_list.get("fonts", {}).items():
            self.load_font(name, font_info["path"], font_info["size"])
            
    def get_memory_usage(self) -> Dict[str, int]:
        """Kaynak yöneticisinin bellek kullanımını döndürür"""
        usage = {
            "textures": sum(tex.get_size()[0] * tex.get_size()[1] * tex.get_bytesize() 
                          for tex in self._textures.values()),
            "sounds": sum(snd.get_length() * 44100 * 2 * 2  # Yaklaşık hesaplama
                        for snd in self._sounds.values()),
            "fonts": len(self._fonts)  # Font sayısı
        }
        return usage 