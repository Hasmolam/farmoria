"""
Taktiksel RPG Oyunu
==================
Engine kullanarak geliştirilmiş izometrik taktik RPG oyunu.
"""

import sys
import os
import pygame

# Engine'i Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import GameState
from engine.graphics import debug_manager
from engine.systems import renderer
from src.scenes.battle_scene import BattleScene

class TacticalRPG:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Taktiksel RPG")
        
        self.game_state = GameState()
        self.debug = debug_manager
        self.battle_scene = BattleScene(10, 10)  # 10x10 grid
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Ekranı ortala
        screen_info = pygame.display.Info()
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{(screen_info.current_w - 800)//2},{(screen_info.current_h - 600)//2}"
        
    def handle_events(self):
        """Oyun olaylarını işle"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        return events
        
    def run(self):
        """Oyun döngüsünü başlat"""
        while self.running:
            # Olayları işle
            events = self.handle_events()
            
            # Güncelle
            dt = self.clock.tick(60) / 1000.0  # 60 FPS
            self.battle_scene.update(dt, events)
            
            # Çiz
            self.screen.fill((50, 50, 50))  # Koyu gri arkaplan
            self.battle_scene.render(self.screen)
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = TacticalRPG()
    game.run() 