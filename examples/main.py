import os
import sys

# Proje kök dizinini Python yoluna ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pygame
import asyncio
from engine.scene import SceneManager
from examples.game_scene import GameScene
from examples.menu_scene import MenuScene

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Farmoria")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Scene Manager'ı başlat
        self.scene_manager = SceneManager(self)
        
    async def initialize(self):
        """Oyun başlangıç ayarları"""
        # Scene'leri oluştur ve ekle
        menu_scene = MenuScene()
        game_scene = GameScene()
        
        self.scene_manager.add_scene("menu", menu_scene)
        self.scene_manager.add_scene("game", game_scene)
        
        # Tüm scene'leri önceden yükle
        print("Menü yükleniyor...")
        await self.scene_manager.preload_scene("menu")
        print("Oyun sahnesi yükleniyor...")
        await self.scene_manager.preload_scene("game")
        print("Yükleme tamamlandı!")
        
        # Menü scene'ini başlat
        self.scene_manager.set_scene("menu")
    
    def handle_events(self):
        """Olay işleme"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scene_manager.handle_event(event)
    
    def update(self, dt: float):
        """Oyun mantığını güncelle"""
        self.scene_manager.update(dt)
    
    def draw(self):
        """Oyunu çiz"""
        self.scene_manager.draw(self.screen)
        pygame.display.flip()
    
    async def run(self):
        """Ana oyun döngüsü"""
        await self.initialize()
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            # Asenkron işlemler için event loop'a zaman ver
            await asyncio.sleep(0)
        
        pygame.quit()

if __name__ == "__main__":
    engine = GameEngine()
    asyncio.run(engine.run()) 