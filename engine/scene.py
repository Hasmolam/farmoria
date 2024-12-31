import pygame
from typing import Dict, Optional, Any, List, Set
from enum import Enum
import logging
from weakref import WeakSet

class SceneError(Exception):
    """Scene ile ilgili hatalar için özel exception sınıfı"""
    pass

class SceneState(Enum):
    LOADING = "loading"
    READY = "ready"
    TRANSITIONING = "transitioning"
    PAUSED = "paused"
    CLEANUP = "cleanup"

class Scene:
    def __init__(self):
        self.engine = None
        self.state = SceneState.LOADING
        self.transition_alpha = 255
        self.data = {}
        self.assets: Set[str] = WeakSet()  # Zayıf referanslar ile asset takibi
        self.is_paused = False
        self.loading_progress = 0.0
        self.is_transitioning = False  # Geçiş durumu için yeni flag
    
    def set_engine(self, engine):
        self.engine = engine
        for child in getattr(self, 'children', []):
            if hasattr(child, 'engine'):
                child.engine = engine
    
    async def preload(self):
        """Scene için gerekli assetlerin ön yüklemesi"""
        self.loading_progress = 0.0
        # Alt sınıflar bu metodu override edebilir
        pass
    
    def on_enter(self, data: Dict[str, Any] = None):
        try:
            self.state = SceneState.READY
            if data:
                self.data = data
        except Exception as e:
            logging.error(f"Scene giriş hatası: {str(e)}")
            raise SceneError(f"Scene başlatılamadı: {str(e)}")
    
    def on_exit(self):
        self.state = SceneState.TRANSITIONING
        self.is_transitioning = True  # Geçişi başlat
        self.cleanup()
    
    def cleanup(self):
        """Scene kaynaklarını temizle"""
        self.state = SceneState.CLEANUP
        self.assets.clear()
        
    def pause(self):
        """Scene'i duraklat"""
        if self.state == SceneState.READY:
            self.state = SceneState.PAUSED
            self.is_paused = True
    
    def resume(self):
        """Scene'i devam ettir"""
        if self.state == SceneState.PAUSED:
            self.state = SceneState.READY
            self.is_paused = False
    
    def update(self, dt: float):
        if self.is_transitioning:  # Geçiş durumunu kontrol et
            self.transition_alpha = max(0, self.transition_alpha - 510 * dt)
            if self.transition_alpha <= 0:
                self.is_transitioning = False
        elif not self.is_paused:
            self._update_scene(dt)
    
    def _update_scene(self, dt: float):
        """Alt sınıfların override edeceği asıl update metodu"""
        pass
    
    def draw(self, screen: pygame.Surface):
        if self.state == SceneState.LOADING:
            self._draw_loading_screen(screen)
        elif not self.is_paused:
            self._draw_scene(screen)
            
        if self.is_transitioning:  # Geçiş durumunu kontrol et
            transition_surface = pygame.Surface(screen.get_size())
            transition_surface.fill((0, 0, 0))
            transition_surface.set_alpha(self.transition_alpha)
            screen.blit(transition_surface, (0, 0))
    
    def _draw_loading_screen(self, screen: pygame.Surface):
        """Yükleme ekranını çiz"""
        # Basit bir yükleme ekranı
        screen.fill((0, 0, 0))
        progress_width = screen.get_width() * 0.8
        progress_height = 20
        progress_x = (screen.get_width() - progress_width) / 2
        progress_y = screen.get_height() / 2
        
        # Yükleme çubuğu arka planı
        pygame.draw.rect(screen, (50, 50, 50), 
                        (progress_x, progress_y, progress_width, progress_height))
        # Yükleme çubuğu
        progress = progress_width * self.loading_progress
        if progress > 0:
            pygame.draw.rect(screen, (100, 200, 100),
                           (progress_x, progress_y, progress, progress_height))
    
    def _draw_scene(self, screen: pygame.Surface):
        """Alt sınıfların override edeceği asıl draw metodu"""
        pass
    
    def handle_event(self, event: pygame.event.Event):
        if not self.is_paused:
            self._handle_scene_event(event)
    
    def _handle_scene_event(self, event: pygame.event.Event):
        """Alt sınıfların override edeceği asıl event handling metodu"""
        pass
    
    def is_ready(self) -> bool:
        return self.state == SceneState.READY

class SceneManager:
    def __init__(self, engine):
        self.engine = engine
        self.scenes: Dict[str, Scene] = {}
        self.scene_stack: List[str] = []  # Scene geçmişi için stack
        self.current_scene: Optional[Scene] = None
        self.next_scene: Optional[str] = None
        self.transition_data: Dict[str, Any] = {}
        self.cached_scenes: Set[str] = set()  # Cache'lenmiş scene'ler
    
    def add_scene(self, name: str, scene: Scene):
        try:
            scene.set_engine(self.engine)
            self.scenes[name] = scene
        except Exception as e:
            logging.error(f"Scene eklenirken hata: {str(e)}")
            raise SceneError(f"Scene eklenemedi: {str(e)}")
    
    async def preload_scene(self, name: str):
        """Belirtilen scene'i arka planda yükle"""
        if name in self.scenes:
            scene = self.scenes[name]
            await scene.preload()
            self.cached_scenes.add(name)
    
    def set_scene(self, name: str, transition_data: Dict[str, Any] = None):
        if name not in self.scenes:
            raise SceneError(f"Scene bulunamadı: {name}")
            
        self.next_scene = name
        self.transition_data = transition_data or {}
        
        if self.current_scene:
            self.current_scene.on_exit()
            self.scene_stack.append(self.get_current_scene_name())
            self._change_scene()
        else:
            self._change_scene()
    
    def pop_scene(self):
        """Stack'teki son scene'e geri dön"""
        if self.scene_stack:
            previous_scene = self.scene_stack.pop()
            self.set_scene(previous_scene)
    
    def _change_scene(self):
        if self.next_scene:
            try:
                old_scene = self.current_scene
                new_scene = self.scenes[self.next_scene]
                
                # Scene henüz cache'lenmediyse yükle
                if self.next_scene not in self.cached_scenes:
                    new_scene.state = SceneState.LOADING
                
                new_scene.on_enter(self.transition_data)
                self.current_scene = new_scene
                self.next_scene = None
                self.transition_data = {}
                
                if old_scene:
                    old_scene.transition_alpha = 255
                    
            except Exception as e:
                logging.error(f"Scene değişimi sırasında hata: {str(e)}")
                raise SceneError(f"Scene değişimi başarısız: {str(e)}")
    
    def update(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)
    
    def draw(self, screen: pygame.Surface):
        if self.current_scene:
            self.current_scene.draw(screen)
    
    def handle_event(self, event: pygame.event.Event):
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def get_current_scene_name(self) -> Optional[str]:
        for name, scene in self.scenes.items():
            if scene == self.current_scene:
                return name
        return None
    
    def pause_current_scene(self):
        """Mevcut scene'i duraklat"""
        if self.current_scene:
            self.current_scene.pause()
    
    def resume_current_scene(self):
        """Mevcut scene'i devam ettir"""
        if self.current_scene:
            self.current_scene.resume()
    
    def clear_cache(self):
        """Cache'lenmiş scene'leri temizle"""
        self.cached_scenes.clear() 