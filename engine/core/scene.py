import pygame
from typing import Dict, List, Optional
from .base import GameObject, GameSystem

class Scene:
    """Oyun sahnesi"""
    def __init__(self, name: str):
        self.name = name
        self.objects: List[GameObject] = []
        self.systems: List[GameSystem] = []
        self.active = False
        self.engine = None
        
    def activate(self):
        """Sahneyi aktifleştirir"""
        self.active = True
        
    def deactivate(self):
        """Sahneyi pasifleştirir"""
        self.active = False
        
    def add_object(self, obj: GameObject):
        """Sahneye nesne ekler"""
        self.objects.append(obj)
        
    def remove_object(self, obj: GameObject):
        """Sahneden nesne kaldırır"""
        if obj in self.objects:
            self.objects.remove(obj)
            
    def add_system(self, system: GameSystem):
        """Sahneye sistem ekler"""
        self.systems.append(system)
        
    def remove_system(self, system: GameSystem):
        """Sahneden sistem kaldırır"""
        if system in self.systems:
            self.systems.remove(system)
            
    def handle_event(self, event: pygame.event.Event):
        """Sahne olaylarını işler"""
        for system in self.systems:
            if hasattr(system, 'handle_event'):
                system.handle_event(event)
                
    def update(self, dt: float):
        """Sahneyi günceller"""
        if not self.active:
            return
            
        for obj in self.objects:
            obj.update(dt)
            
        for system in self.systems:
            system.update(dt)
            
    def draw(self, surface: pygame.Surface):
        """Sahneyi çizer"""
        if not self.active:
            return
            
        for obj in self.objects:
            obj.draw(surface)
            
        for system in self.systems:
            system.draw(surface)
            
    def on_enter(self):
        """Sahne aktif olduğunda çağrılır"""
        self.active = True
        
    def on_exit(self):
        """Sahne pasif olduğunda çağrılır"""
        self.active = False

class SceneManager:
    """Sahne yönetimi sınıfı"""
    
    def __init__(self, engine):
        """SceneManager başlatıcı"""
        self.engine = engine
        self.scenes = {}
        self.active_scene = None
        
    def add_scene(self, scene):
        """Yeni bir sahne ekler"""
        self.scenes[scene.name] = scene
        scene.manager = self
        
    def get_scene(self, name):
        """İsme göre sahne getirir"""
        return self.scenes.get(name)
        
    def set_scene(self, name):
        """Aktif sahneyi değiştirir"""
        if name in self.scenes:
            if self.active_scene:
                self.active_scene.deactivate()
            self.active_scene = self.scenes[name]
            self.active_scene.activate()
        else:
            raise ValueError(f"Scene '{name}' not found")
        
    def remove_scene(self, name):
        """Sahne siler"""
        if name in self.scenes:
            if self.active_scene == self.scenes[name]:
                self.active_scene.deactivate()
                self.active_scene = None
            del self.scenes[name]
            
    def activate_scene(self, name):
        """Sahneyi aktifleştirir"""
        if name in self.scenes:
            if self.active_scene:
                self.active_scene.deactivate()
            self.active_scene = self.scenes[name]
            self.active_scene.activate()
            
    def deactivate_scene(self, name):
        """Sahneyi pasifleştirir"""
        if name in self.scenes:
            self.scenes[name].deactivate()
            if self.active_scene == self.scenes[name]:
                self.active_scene = None 