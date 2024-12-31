import pygame
import os
from typing import Dict, Optional
from enum import Enum, auto

class AudioType(Enum):
    """Ses türleri için enum"""
    MUSIC = auto()
    SOUND = auto()

class AudioSystem:
    def __init__(self):
        """Ses sistemini başlat"""
        pygame.mixer.init()
        
        # Ses ayarları
        self.music_volume = 1.0
        self.sound_volume = 1.0
        
        # Yüklenen sesler
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        
        # Ses kanalları
        self.channels: Dict[str, pygame.mixer.Channel] = {}
        for i in range(8):  # 8 kanal oluştur
            self.channels[f"channel_{i}"] = pygame.mixer.Channel(i)
    
    def load_sound(self, name: str, file_path: str) -> None:
        """Ses efekti yükle"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Ses dosyası bulunamadı: {file_path}")
            
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
        except pygame.error as e:
            raise Exception(f"Ses yüklenirken hata: {str(e)}")
    
    def play_sound(self, name: str, loop: int = 0, channel: Optional[str] = None) -> None:
        """Ses efekti çal"""
        if name not in self.sounds:
            raise KeyError(f"Ses bulunamadı: {name}")
            
        sound = self.sounds[name]
        sound.set_volume(self.sound_volume)
        
        if channel and channel in self.channels:
            self.channels[channel].play(sound, loops=loop)
        else:
            sound.play(loops=loop)
    
    def load_music(self, file_path: str) -> None:
        """Müzik dosyası yükle"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Müzik dosyası bulunamadı: {file_path}")
            
        try:
            pygame.mixer.music.load(file_path)
            self.current_music = file_path
        except pygame.error as e:
            raise Exception(f"Müzik yüklenirken hata: {str(e)}")
    
    def play_music(self, loop: int = -1) -> None:
        """Müzik çal"""
        if not self.current_music:
            return
            
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(loops=loop)
    
    def stop_music(self) -> None:
        """Müziği durdur"""
        pygame.mixer.music.stop()
    
    def pause_music(self) -> None:
        """Müziği duraklat"""
        pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Müziği devam ettir"""
        pygame.mixer.music.unpause()
    
    def fade_out_music(self, time_ms: int) -> None:
        """Müziği yavaşça kapat"""
        pygame.mixer.music.fadeout(time_ms)
    
    def set_music_volume(self, volume: float) -> None:
        """Müzik ses seviyesini ayarla (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume: float) -> None:
        """Ses efektleri ses seviyesini ayarla (0.0 - 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def stop_channel(self, channel: str) -> None:
        """Belirli bir kanalı durdur"""
        if channel in self.channels:
            self.channels[channel].stop()
    
    def stop_all_sounds(self) -> None:
        """Tüm ses efektlerini durdur"""
        pygame.mixer.stop()
    
    def is_music_playing(self) -> bool:
        """Müzik çalıyor mu kontrol et"""
        return pygame.mixer.music.get_busy()
    
    def get_music_pos(self) -> float:
        """Müziğin şu anki pozisyonunu al (saniye)"""
        return pygame.mixer.music.get_pos() / 1000.0
    
    def cleanup(self) -> None:
        """Ses sistemini temizle"""
        pygame.mixer.quit() 