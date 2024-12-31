import pygame
import time
from typing import Optional

class Timer:
    """Zamanlama yönetimi"""
    def __init__(self, target_fps: int = 60, vsync: bool = True):
        self.target_fps = target_fps
        self.vsync = vsync
        self.frame_duration = 1.0 / target_fps
        self.last_time = time.perf_counter()
        self.delta_time = 0.0
        self.accumulated_time = 0.0
        self.frame_count = 0
        self.fps = 0.0
        self.fps_update_time = 0.0
        
        # V-Sync'i ayarla
        if vsync:
            # V-Sync'i etkinleştir (OpenGL olmadan)
            pygame.display.set_mode(
                pygame.display.get_surface().get_size(),
                pygame.DOUBLEBUF | pygame.HWSURFACE
            )
            pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    
    def tick(self) -> float:
        """Frame süresini hesapla ve FPS'i güncelle"""
        current_time = time.perf_counter()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        # Delta time'ı hesapla ve sınırla
        self.delta_time = min(frame_time, 0.1)  # En fazla 100ms gecikme
        
        # FPS hesaplama
        self.frame_count += 1
        self.accumulated_time += frame_time
        
        # Her saniye FPS'i güncelle
        if current_time - self.fps_update_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.fps_update_time)
            self.frame_count = 0
            self.fps_update_time = current_time
        
        # V-Sync kapalıysa FPS sınırlama uygula
        if not self.vsync:
            # Hedef FPS için bekleme süresi
            target_frame_time = self.frame_duration
            if frame_time < target_frame_time:
                time.sleep(target_frame_time - frame_time)
        
        return self.delta_time
    
    def get_fps(self) -> float:
        """Güncel FPS değerini döndür"""
        return self.fps
    
    def get_frame_duration(self) -> float:
        """Hedef frame süresini döndür"""
        return self.frame_duration
    
    def set_target_fps(self, fps: int):
        """Hedef FPS'i ayarla"""
        self.target_fps = fps
        self.frame_duration = 1.0 / fps
    
    def toggle_vsync(self):
        """V-Sync'i aç/kapa"""
        self.vsync = not self.vsync
        # V-Sync ayarlarını güncelle (OpenGL olmadan)
        pygame.display.set_mode(
            pygame.display.get_surface().get_size(),
            pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

class FrameManager:
    """Frame yönetimi"""
    def __init__(self, timer: Timer):
        self.timer = timer
        self.fixed_update_rate = 1.0 / 50.0  # Fizik güncellemesi için sabit oran (50 Hz)
        self.accumulated_time = 0.0
        self.max_updates_per_frame = 5  # Bir frame'de maksimum güncelleme sayısı
    
    def update(self, update_func, render_func):
        """Frame güncellemesi ve çizimi"""
        # Delta time'ı al
        dt = self.timer.tick()
        
        # Birikmiş zamanı güncelle
        self.accumulated_time += dt
        
        # Sabit oranlı güncellemeler
        update_count = 0
        while self.accumulated_time >= self.fixed_update_rate and update_count < self.max_updates_per_frame:
            update_func(self.fixed_update_rate)
            self.accumulated_time -= self.fixed_update_rate
            update_count += 1
        
        # Çok fazla güncelleme birikirse sıfırla
        if self.accumulated_time > self.fixed_update_rate * self.max_updates_per_frame:
            self.accumulated_time = 0.0
        
        # Render
        render_func()
        
        # V-Sync kapalıysa ekranı güncelle
        if not self.timer.vsync:
            pygame.display.flip()
    
    def set_fixed_update_rate(self, rate: float):
        """Sabit güncelleme oranını ayarla"""
        self.fixed_update_rate = 1.0 / rate 