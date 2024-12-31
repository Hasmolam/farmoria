import pygame
from typing import Dict, Optional
from ..core.base import GameSystem

class AudioSystem(GameSystem):
    """Ses sistemi"""
    def __init__(self):
        super().__init__("AudioSystem")
        pygame.mixer.init()
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 1.0
        self.sound_volume = 1.0
        
    def load_sound(self, name: str, file_path: str) -> bool:
        """Ses efekti yükler"""
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"Ses yüklenirken hata: {e}")
            return False
            
    def play_sound(self, name: str, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> Optional[pygame.mixer.Channel]:
        """Ses efekti çalar"""
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(self.sound_volume)
            return sound.play(loops, maxtime, fade_ms)
        return None
        
    def stop_sound(self, name: str):
        """Ses efektini durdurur"""
        if name in self.sounds:
            self.sounds[name].stop()
            
    def play_music(self, file_path: str, loops: int = -1, start: float = 0.0, fade_ms: int = 0):
        """Müzik çalar"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops, start, fade_ms)
        except Exception as e:
            print(f"Müzik çalınırken hata: {e}")
            
    def stop_music(self, fade_ms: int = 0):
        """Müziği durdurur"""
        pygame.mixer.music.fadeout(fade_ms)
        
    def pause_music(self):
        """Müziği duraklatır"""
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """Müziği devam ettirir"""
        pygame.mixer.music.unpause()
        
    def set_music_volume(self, volume: float):
        """Müzik ses seviyesini ayarlar"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
    def set_sound_volume(self, volume: float):
        """Ses efektleri ses seviyesini ayarlar"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
            
    def get_music_volume(self) -> float:
        """Müzik ses seviyesini döndürür"""
        return self.music_volume
        
    def get_sound_volume(self) -> float:
        """Ses efektleri ses seviyesini döndürür"""
        return self.sound_volume
        
    def is_music_playing(self) -> bool:
        """Müzik çalıyor mu kontrol eder"""
        return pygame.mixer.music.get_busy()
        
    def cleanup(self):
        """Ses sistemini temizler"""
        pygame.mixer.music.stop()
        pygame.mixer.quit() 