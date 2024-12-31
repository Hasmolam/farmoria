import pygame
import pymunk
import sys
import os

# Engine modülünü import edebilmek için path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.physics import PhysicsWorld
from engine.base import GameObject

# Pygame başlat
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Fizik Test")
clock = pygame.time.Clock()

# Fizik dünyası oluştur
world = PhysicsWorld()

# Test nesnesi oluştur
class TestBall(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.color = (255, 0, 0)
        self.bounce = 0.5
        self.mass = 1.0
        self.friction = 0.3
        self.radius = 20

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, 
                         (int(self.position.x), int(self.position.y)), 
                         self.radius)

# Test nesnelerini oluştur
balls = []
for i in range(5):
    ball = TestBall(200 + i * 100, 100)
    world.add_body(ball)
    balls.append(ball)

# Ana döngü
running = True
while running:
    # Event'leri işle
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Tıklanan yerde yeni top oluştur
            pos = pygame.mouse.get_pos()
            ball = TestBall(pos[0], pos[1])
            world.add_body(ball)
            balls.append(ball)
            
    # Fizik dünyasını güncelle
    world.update(1.0 / 60.0)
    
    # Ekranı temizle
    screen.fill((135, 206, 235))  # Açık mavi
    
    # Zemini çiz
    pygame.draw.line(screen, (0, 255, 0), 
                    (0, world.ground_level), 
                    (screen.get_width(), world.ground_level), 
                    2)
    pygame.draw.rect(screen, (0, 255, 0),
                    (0, world.ground_level + 2,
                     screen.get_width(),
                     screen.get_height() - world.ground_level))
    
    # Nesneleri çiz
    for ball in balls:
        ball.draw(screen)
    
    # Debug çizimi
    world.draw_debug(screen)
    
    # Ekranı güncelle
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 