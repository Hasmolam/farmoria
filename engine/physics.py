import pygame
import pymunk
import math

class CollisionType:
    PLAYER = 1
    PLATFORM = 2
    ENEMY = 3
    ITEM = 4

class PhysicsWorld:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.collision_handlers = {}
        self.debug_draw = True
    
    def set_gravity(self, gravity):
        """Yerçekimini ayarla"""
        self.space.gravity = gravity
    
    def create_box(self, pos, size, mass=1.0):
        """Kutu oluştur"""
        moment = pymunk.moment_for_box(mass, size)
        body = pymunk.Body(mass, moment)
        body.position = pos
        
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 0.7
        shape.elasticity = 0.2
        
        self.space.add(body, shape)
        return body, shape
    
    def apply_material(self, shape, material):
        """Şekle materyal uygula"""
        materials = {
            'metal': {'friction': 0.4, 'elasticity': 0.5},
            'wood': {'friction': 0.7, 'elasticity': 0.2},
            'ice': {'friction': 0.1, 'elasticity': 0.8},
            'rubber': {'friction': 0.9, 'elasticity': 0.9}
        }
        
        if material in materials:
            props = materials[material]
            shape.friction = props['friction']
            shape.elasticity = props['elasticity']
    
    def add_collision_callback(self, type_a, type_b, callback):
        """Çarpışma callback'i ekle"""
        def _handler(arbiter, space, data):
            callback(arbiter.shapes[0], arbiter.shapes[1])
            return True
            
        handler = self.space.add_collision_handler(type_a, type_b)
        handler.separate = _handler
        self.collision_handlers[(type_a, type_b)] = handler
    
    def update(self, dt):
        """Fizik dünyasını güncelle"""
        self.space.step(dt)
    
    def draw_debug(self, screen):
        """Debug görselleştirme"""
        if not self.debug_draw:
            return
            
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Poly):
                try:
                    points = [p.rotated(shape.body.angle) + shape.body.position for p in shape.get_vertices()]
                    points = [(int(p.x), int(p.y)) for p in points if not (math.isnan(p.x) or math.isnan(p.y))]
                    if len(points) > 2:
                        pygame.draw.polygon(screen, (200, 200, 200), points, 2)
                except (ValueError, AttributeError):
                    continue
    
    def clear(self):
        """Fizik dünyasını temizle"""
        for body in self.space.bodies:
            self.space.remove(body)
        for shape in self.space.shapes:
            self.space.remove(shape)
        self.collision_handlers.clear() 