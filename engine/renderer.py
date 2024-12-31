import pygame
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging

@dataclass
class RenderObject:
    surface: pygame.Surface
    position: Tuple[float, float]
    layer: int = 0
    alpha: int = 255
    visible: bool = True
    scale: Tuple[float, float] = (1.0, 1.0)
    rotation: float = 0.0

class RenderLayer:
    def __init__(self, layer_id: int):
        self.layer_id = layer_id
        self.objects: List[RenderObject] = []
        self.visible = True
        self.alpha = 255

    def add_object(self, obj: RenderObject):
        self.objects.append(obj)

    def remove_object(self, obj: RenderObject):
        if obj in self.objects:
            self.objects.remove(obj)

class Renderer:
    def __init__(self):
        self.layers: Dict[int, RenderLayer] = {}
        self.camera_pos = [0, 0]
        self.camera_zoom = 1.0
        self.post_processing_effects = []

    def create_layer(self, layer_id: int) -> RenderLayer:
        if layer_id not in self.layers:
            self.layers[layer_id] = RenderLayer(layer_id)
        return self.layers[layer_id]

    def add_object(self, obj: RenderObject):
        if obj.layer not in self.layers:
            self.create_layer(obj.layer)
        self.layers[obj.layer].add_object(obj)

    def remove_object(self, obj: RenderObject):
        if obj.layer in self.layers:
            self.layers[obj.layer].remove_object(obj)

    def set_camera(self, x: float, y: float):
        self.camera_pos = [x, y]

    def move_camera(self, dx: float, dy: float):
        self.camera_pos[0] += dx
        self.camera_pos[1] += dy

    def set_zoom(self, zoom: float):
        self.camera_zoom = max(0.1, min(10.0, zoom))

    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        screen_x = (x - self.camera_pos[0]) * self.camera_zoom
        screen_y = (y - self.camera_pos[1]) * self.camera_zoom
        return screen_x, screen_y

    def render(self, target_surface: pygame.Surface):
        # Katmanları sırala ve çiz
        sorted_layers = sorted(self.layers.items(), key=lambda x: x[0])
        
        for layer_id, layer in sorted_layers:
            if not layer.visible:
                continue

            for obj in layer.objects:
                if not obj.visible:
                    continue

                # Objenin ekran pozisyonunu hesapla
                screen_x, screen_y = self.world_to_screen(*obj.position)
                
                # Ölçekleme ve rotasyon varsa uygula
                if obj.scale != (1.0, 1.0) or obj.rotation != 0.0:
                    scaled_surface = pygame.transform.scale(
                        obj.surface,
                        (obj.surface.get_width() * obj.scale[0],
                         obj.surface.get_height() * obj.scale[1])
                    )
                    if obj.rotation != 0.0:
                        scaled_surface = pygame.transform.rotate(scaled_surface, obj.rotation)
                else:
                    scaled_surface = obj.surface

                # Alpha değerini ayarla
                if obj.alpha < 255:
                    scaled_surface.set_alpha(obj.alpha)

                # Objeyi çiz
                target_surface.blit(scaled_surface, (screen_x, screen_y))

        # Post-processing efektlerini uygula
        for effect in self.post_processing_effects:
            effect.apply(target_surface) 