import pygame
from typing import Tuple, Dict, Any, Optional

class Vector2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

class GameObject:
    """Oyun nesnelerinin temel sınıfı"""
    def __init__(self):
        self.position = Vector2()
        self.velocity = Vector2()
        self.angle = 0
        self.scale = Vector2(1, 1)
        self.active = True
        self.z_index = 0
        self.engine = None
        
    def update(self, dt: float) -> None:
        """Her karede çağrılır"""
        pass
        
    def draw(self, screen: pygame.Surface) -> None:
        """Her karede çizim için çağrılır"""
        pass
        
    def serialize(self) -> Dict[str, Any]:
        """Nesneyi kaydetmek için serileştir"""
        return {
            'position_x': self.position.x,
            'position_y': self.position.y,
            'velocity_x': self.velocity.x,
            'velocity_y': self.velocity.y,
            'angle': self.angle,
            'scale_x': self.scale.x,
            'scale_y': self.scale.y,
            'active': self.active,
            'z_index': self.z_index
        }
        
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Kaydedilmiş veriden nesneyi yükle"""
        self.position.x = data.get('position_x', 0)
        self.position.y = data.get('position_y', 0)
        self.velocity.x = data.get('velocity_x', 0)
        self.velocity.y = data.get('velocity_y', 0)
        self.angle = data.get('angle', 0)
        self.scale.x = data.get('scale_x', 1)
        self.scale.y = data.get('scale_y', 1)
        self.active = data.get('active', True)
        self.z_index = data.get('z_index', 0)

class GameSystem:
    """Oyun sistemlerinin temel sınıfı"""
    def __init__(self, name: str):
        self.name = name
        self.active = True
        self.engine = None
        
    def update(self, dt: float) -> None:
        """Her karede çağrılır"""
        pass
        
    def serialize(self) -> Dict[str, Any]:
        """Sistemi kaydetmek için serileştir"""
        return {
            'name': self.name,
            'active': self.active
        }
        
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Kaydedilmiş veriden sistemi yükle"""
        self.name = data.get('name', '')
        self.active = data.get('active', True)

class PhysicsBody(GameObject):
    def __init__(self, x: float = 0, y: float = 0):
        super().__init__()
        self.position = Vector2(x, y)
        self.velocity = Vector2()
        self.mass = 1.0
        self.radius = 20
        self.friction = 0.7
        self.bounce = 0.5
        self.pymunk_body = None
        self.pymunk_shape = None
        
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            'mass': self.mass,
            'radius': self.radius,
            'friction': self.friction,
            'bounce': self.bounce
        })
        return data
        
    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self.mass = data.get('mass', 1.0)
        self.radius = data.get('radius', 20)
        self.friction = data.get('friction', 0.7)
        self.bounce = data.get('bounce', 0.5) 