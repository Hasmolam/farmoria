"""
Fizik sistemi modülü.
Pymunk kullanarak 2D fizik simülasyonunu yönetir.
"""

import pymunk
from typing import Dict, Optional, Tuple
from ..core.base import GameSystem, GameObject

class PhysicsBody:
    """Fizik nesnesi sınıfı"""
    
    def __init__(self, body_type: str = "dynamic", mass: float = 1.0, moment: float = 100):
        """
        PhysicsBody başlatıcı
        
        Args:
            body_type: Gövde tipi ("dynamic", "static", "kinematic")
            mass: Kütle (kg)
            moment: Eylemsizlik momenti
        """
        if body_type == "static":
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        elif body_type == "kinematic":
            self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        else:
            self.body = pymunk.Body(mass, moment)
            
        self.shapes: list[pymunk.Shape] = []
        
    def add_circle_shape(self, radius: float, offset: Tuple[float, float] = (0, 0), 
                        friction: float = 0.7, elasticity: float = 0.5):
        """Daire şekli ekler"""
        shape = pymunk.Circle(self.body, radius, offset)
        shape.friction = friction
        shape.elasticity = elasticity
        self.shapes.append(shape)
        return shape
        
    def add_box_shape(self, width: float, height: float, offset: Tuple[float, float] = (0, 0),
                      friction: float = 0.7, elasticity: float = 0.5):
        """Kutu şekli ekler"""
        shape = pymunk.Poly.create_box(self.body, size=(width, height))
        shape.friction = friction
        shape.elasticity = elasticity
        self.shapes.append(shape)
        return shape
        
    def add_poly_shape(self, vertices: list[Tuple[float, float]], offset: Tuple[float, float] = (0, 0),
                       friction: float = 0.7, elasticity: float = 0.5):
        """Çokgen şekli ekler"""
        shape = pymunk.Poly(self.body, vertices, transform=pymunk.Transform.identity())
        shape.friction = friction
        shape.elasticity = elasticity
        self.shapes.append(shape)
        return shape
        
    @property
    def position(self) -> Tuple[float, float]:
        """Pozisyonu döndürür"""
        return self.body.position.x, self.body.position.y
        
    @position.setter
    def position(self, pos: Tuple[float, float]):
        """Pozisyonu ayarlar"""
        self.body.position = pos
        
    @property
    def angle(self) -> float:
        """Açıyı döndürür"""
        return self.body.angle
        
    @angle.setter
    def angle(self, angle: float):
        """Açıyı ayarlar"""
        self.body.angle = angle
        
    def apply_force(self, force: Tuple[float, float], point: Tuple[float, float] = None):
        """Kuvvet uygular"""
        if point:
            self.body.apply_force_at_world_point(force, point)
        else:
            self.body.apply_force_at_local_point(force, (0, 0))
            
        # Kuvvet uygulandıktan sonra bir adım simülasyon yap
        space = self.body.space
        if space:
            space.step(1/60.0)
        
    def apply_impulse(self, impulse: Tuple[float, float], point: Tuple[float, float] = None):
        """Impuls uygular"""
        if point:
            self.body.apply_impulse_at_world_point(impulse, point)
        else:
            self.body.apply_impulse_at_local_point(impulse, (0, 0))

class PhysicsSystem(GameSystem):
    """Fizik sistemi"""
    
    def __init__(self):
        super().__init__("PhysicsSystem")
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.bodies: Dict[str, PhysicsBody] = {}
        
    def create_body(self, name: str, body_type: str = "dynamic", mass: float = 1.0, 
                   moment: float = 100) -> PhysicsBody:
        """Yeni fizik gövdesi oluşturur"""
        body = PhysicsBody(body_type, mass, moment)
        self.space.add(body.body)
        self.bodies[name] = body
        
        # Şekil ekle (varsayılan olarak küçük bir kutu)
        body.add_box_shape(10, 10)
        for shape in body.shapes:
            self.space.add(shape)
            
        return body
        
    def remove_body(self, name: str):
        """Fizik gövdesini kaldırır"""
        if name in self.bodies:
            body = self.bodies[name]
            for shape in body.shapes:
                self.space.remove(shape)
            self.space.remove(body.body)
            del self.bodies[name]
            
    def get_body(self, name: str) -> Optional[PhysicsBody]:
        """İsme göre fizik gövdesi döndürür"""
        return self.bodies.get(name)
        
    def update(self, dt: float):
        """Fizik sistemini günceller"""
        # Daha hassas simülasyon için küçük adımlarla güncelle
        steps = 10
        step_dt = dt / steps
        for _ in range(steps):
            self.space.step(step_dt)
        
    def add_collision_handler(self, type_a: int, type_b: int):
        """Çarpışma yöneticisi ekler"""
        return self.space.add_collision_handler(type_a, type_b)
        
    def set_gravity(self, x: float, y: float):
        """Yerçekimini ayarlar"""
        self.space.gravity = (x, y)
        
    def clear(self):
        """Tüm fizik gövdelerini temizler"""
        for name in list(self.bodies.keys()):
            self.remove_body(name) 