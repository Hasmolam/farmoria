import pygame
import pymunk
from typing import Optional
from .scene import SceneManager
from .base import GameObject, GameSystem
from .audio import AudioSystem
from .ui import UIManager
from .renderer import Renderer

class FarmoriaEngine:
    def __init__(self, width: int, height: int, title: str):
        pygame.init()
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode((width, height), flags, vsync=1)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene_manager = SceneManager(self)
        self.audio_system = AudioSystem()
        self.ui_manager = UIManager()
        self.ui_manager.set_engine(self)
        self.renderer = Renderer()
        
    def add_scene(self, scene):
        self.scene_manager.add_scene(scene)
        
    def set_scene(self, scene_name: str):
        self.scene_manager.set_scene(scene_name)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                # Önce UI Manager'a gönder
                handled = self.ui_manager.handle_event(event)
                # UI işlemediyse Scene'e gönder
                if not handled:
                    self.scene_manager.handle_event(event)
                
    def update(self, dt: float):
        self.scene_manager.update(dt)
        self.ui_manager.update(dt)
        
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        self.renderer.render(self.screen)
        self.ui_manager.draw(self.screen)
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS hedefi
            self.handle_events()
            self.update(dt)
            self.draw()
            
        self.audio_system.cleanup()
        pygame.quit() 