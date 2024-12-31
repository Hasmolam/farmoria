"""
Taktiksel savaş sahnesi.
İzometrik grid sistemi ve karakter yönetimini içerir.
"""

import pygame
from engine.core import GameObject
from engine.systems import renderer
from typing import List, Tuple, Dict, Optional
from ..entities.character import Character
from ..core.grid import IsometricGrid, Tile
from ..core.turn_manager import TurnManager
from ..core.camera import Camera
import math

class BattleScene(GameObject):
    """Taktiksel savaş sahnesi"""
    def __init__(self, width: int = 10, height: int = 10):
        super().__init__()
        self.grid = IsometricGrid()
        self.width = width
        self.height = height
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.selected_tile = None
        self.characters: List[Character] = []
        self.selected_character: Optional[Character] = None
        self.turn_manager = TurnManager()
        
        # Grid'i ekranın ortasına yerleştirmek için offset
        self.offset_x = 400 - (width * self.grid.tile_width/4)
        self.offset_y = 300 - (height * self.grid.tile_height/4)
        
        # Kamera sistemi
        self.camera = Camera(800, 600)  # Ekran boyutları
        
        # Font
        self.font = pygame.font.SysFont('Arial', 24)
        
        self.init_grid()
        self.init_characters()
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Dünya koordinatlarını ekran koordinatlarına çevirir"""
        # Önce grid offset'i uygula
        screen_x = world_x + self.offset_x
        screen_y = world_y + self.offset_y
        # Sonra kamera dönüşümü uygula
        return self.camera.apply((screen_x, screen_y))
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Ekran koordinatlarını dünya koordinatlarına çevirir"""
        # Önce kamera dönüşümünü geri al
        world_x, world_y = self.camera.unapply((screen_x, screen_y))
        # Sonra grid offset'ini çıkar
        return world_x - self.offset_x, world_y - self.offset_y
    
    def update(self, dt: float, events: list):
        """Sahneyi günceller"""
        # Kamera kontrollerini işle
        self.camera.handle_input(events)
        
        mouse_pos = pygame.mouse.get_pos()
        # Mouse pozisyonunu dünya koordinatlarına çevir
        world_pos = self.screen_to_world(*mouse_pos)
        grid_pos = self.grid.iso_to_cart(*world_pos)
        
        # Tuş kontrolleri
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Boşluk tuşu ile turu bitir
                    if self.turn_manager.can_end_turn():
                        next_char = self.turn_manager.next_turn()
                        if next_char:
                            self.selected_character = next_char
                            next_char.selected = True
                
                # Yetenek tuşları (1-4)
                if self.selected_character and self.selected_character == self.turn_manager.get_current_character():
                    skill_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
                    for i, key in enumerate(skill_keys):
                        if event.key == key and i < len(self.selected_character.skills):
                            skill = self.selected_character.skills[i]
                            if not self.selected_character.used_skill_this_turn and skill.current_cooldown == 0:
                                if (grid_pos[0], grid_pos[1]) in self.tiles:
                                    self.selected_character.use_skill(skill, grid_pos)
        
        # Mouse tıklaması kontrolü
        if pygame.mouse.get_pressed()[0]:  # Sol tık
            if (grid_pos[0], grid_pos[1]) in self.tiles:
                clicked_tile = self.tiles[grid_pos]
                clicked_char = self.get_character_at(*grid_pos)
                
                current_char = self.turn_manager.get_current_character()
                
                if clicked_char:
                    if self.selected_character and self.selected_character == current_char:
                        if clicked_char != current_char:
                            # Saldırı kontrolü
                            if self.selected_character.can_attack(clicked_char):
                                self.selected_character.attack(clicked_char)
                                if clicked_char.hp <= 0:
                                    # Karakter öldü
                                    self.remove_character(clicked_char)
                    elif clicked_char == current_char:
                        # Karakter seçimi (sadece sırası gelen karakter seçilebilir)
                        if self.selected_character:
                            self.selected_character.selected = False
                        self.selected_character = clicked_char
                        clicked_char.selected = True
                elif self.selected_character and clicked_tile and self.selected_character == current_char:
                    # Karakter hareketi (sadece sırası gelen karakter hareket edebilir)
                    self.selected_character.move_to(clicked_tile)
        
        # Sağ tık ile seçimi iptal et
        if pygame.mouse.get_pressed()[2]:  # Sağ tık
            if self.selected_character:
                self.selected_character.selected = False
                self.selected_character = None
    
    def render(self, surface: pygame.Surface):
        """Sahneyi render eder"""
        # Tüm karoları çiz
        for tile in self.tiles.values():
            screen_x, screen_y = tile.get_screen_pos()
            screen_x, screen_y = self.world_to_screen(screen_x, screen_y)
            
            # İzometrik karo köşe noktaları
            points = [
                (screen_x, screen_y + self.grid.tile_height/2 * self.camera.zoom),
                (screen_x + self.grid.tile_width/2 * self.camera.zoom, screen_y),
                (screen_x, screen_y - self.grid.tile_height/2 * self.camera.zoom),
                (screen_x - self.grid.tile_width/2 * self.camera.zoom, screen_y)
            ]
            
            pygame.draw.polygon(surface, tile.color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 1)
            
        # Seçili karakterin hareket alanını vurgula
        current_char = self.turn_manager.get_current_character()
        if self.selected_character and self.selected_character == current_char and not self.selected_character.moved_this_turn:
            self.render_movement_range(surface)
            
        # Seçili karakterin saldırı menzilini göster
        if self.selected_character and self.selected_character == current_char and not self.selected_character.attacked_this_turn:
            self.render_attack_range(surface)
            
        # Tüm karakterleri çiz
        for character in self.characters:
            screen_x, screen_y = character.get_screen_pos()
            screen_x, screen_y = self.world_to_screen(screen_x, screen_y)
            
            # Karakter çemberi
            size = character.size * self.camera.zoom
            pygame.draw.circle(surface, character.color, (int(screen_x), int(screen_y)), int(size))
            
            # Yön göstergesi
            direction_rad = math.radians(character.direction)
            end_x = screen_x + size * math.cos(direction_rad)
            end_y = screen_y + size * math.sin(direction_rad)
            pygame.draw.line(surface, (0, 0, 0), (screen_x, screen_y), (end_x, end_y), max(1, int(3 * self.camera.zoom)))
            
            # Seçili durumu
            if character.selected:
                pygame.draw.circle(surface, (255, 255, 0), (int(screen_x), int(screen_y)), 
                                 int(size + 4 * self.camera.zoom), max(1, int(2 * self.camera.zoom)))
                
            # HP göstergesi
            hp_width = 40 * self.camera.zoom
            hp_height = 4 * self.camera.zoom
            hp_x = screen_x - hp_width/2
            hp_y = screen_y - size - 10 * self.camera.zoom
            
            # HP arkaplan
            pygame.draw.rect(surface, (255, 0, 0), 
                            (hp_x, hp_y, hp_width, hp_height))
            
            # Mevcut HP
            current_width = (character.hp / character.max_hp) * hp_width
            pygame.draw.rect(surface, (0, 255, 0), 
                            (hp_x, hp_y, current_width, hp_height))
            
            # Karakter ismi
            name_surface = pygame.font.SysFont('Arial', int(24 * self.camera.zoom)).render(
                character.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(centerx=screen_x, bottom=screen_y - size - 15 * self.camera.zoom)
            surface.blit(name_surface, name_rect)
            
        # Sıradaki karakteri göster (UI elemanları zoom etkilenmez)
        if current_char:
            text = f"Sıra: {current_char.name}"
            if self.turn_manager.can_end_turn():
                text += " (Turu bitirmek için SPACE)"
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (10, 10))
            
            # Seçili karakter bilgileri
            if self.selected_character:
                y_offset = 40
                # Temel özellikler
                stats_text = f"HP: {self.selected_character.hp}/{self.selected_character.max_hp} | " \
                           f"Saldırı: {self.selected_character.attack_power} | " \
                           f"Savunma: {self.selected_character.defense} | " \
                           f"Hareket: {self.selected_character.movement} | " \
                           f"Menzil: {self.selected_character.attack_range}"
                stats_surface = self.font.render(stats_text, True, (255, 255, 255))
                surface.blit(stats_surface, (10, y_offset))
                
                # Yetenekler
                y_offset += 30
                skill_text = "Yetenekler (1-4):"
                skill_surface = self.font.render(skill_text, True, (255, 255, 255))
                surface.blit(skill_surface, (10, y_offset))
                
                for i, skill in enumerate(self.selected_character.skills):
                    y_offset += 25
                    cooldown_text = f" (Bekleme: {skill.current_cooldown})" if skill.current_cooldown > 0 else ""
                    skill_text = f"{i+1}. {skill.name}: {skill.description}{cooldown_text}"
                    skill_surface = self.font.render(skill_text, True, 
                                                   (150, 150, 150) if skill.current_cooldown > 0 else (255, 255, 255))
                    surface.blit(skill_surface, (10, y_offset))
                
                # Aktif etkiler
                if self.selected_character.buffs:
                    y_offset += 35
                    buff_text = "Aktif Etkiler:"
                    buff_surface = self.font.render(buff_text, True, (255, 255, 255))
                    surface.blit(buff_surface, (10, y_offset))
                    
                    for buff_name, turns_left in self.selected_character.buffs.items():
                        y_offset += 25
                        buff_text = f"{buff_name}: {turns_left} tur"
                        buff_surface = self.font.render(buff_text, True, (200, 200, 200))
                        surface.blit(buff_surface, (10, y_offset))
    
    def render_movement_range(self, surface: pygame.Surface):
        """Seçili karakterin hareket menzilini gösterir"""
        if not self.selected_character:
            return
            
        char = self.selected_character
        movement = char.movement
        
        for dx in range(-movement, movement + 1):
            for dy in range(-movement, movement + 1):
                if abs(dx) + abs(dy) <= movement:
                    grid_x = char.grid_x + dx
                    grid_y = char.grid_y + dy
                    
                    tile = self.tiles.get((grid_x, grid_y))
                    if tile and tile.walkable and not tile.occupied:
                        screen_x, screen_y = tile.get_screen_pos()
                        screen_x, screen_y = self.world_to_screen(screen_x, screen_y)
                        
                        points = [
                            (screen_x, screen_y + self.grid.tile_height/2 * self.camera.zoom),
                            (screen_x + self.grid.tile_width/2 * self.camera.zoom, screen_y),
                            (screen_x, screen_y - self.grid.tile_height/2 * self.camera.zoom),
                            (screen_x - self.grid.tile_width/2 * self.camera.zoom, screen_y)
                        ]
                        pygame.draw.polygon(surface, (100, 200, 255, 128), points, max(1, int(2 * self.camera.zoom)))
    
    def render_attack_range(self, surface: pygame.Surface):
        """Seçili karakterin saldırı menzilini gösterir"""
        if not self.selected_character:
            return
            
        char = self.selected_character
        attack_range = char.attack_range
        
        for dx in range(-attack_range, attack_range + 1):
            for dy in range(-attack_range, attack_range + 1):
                if abs(dx) + abs(dy) <= attack_range:
                    grid_x = char.grid_x + dx
                    grid_y = char.grid_y + dy
                    
                    tile = self.tiles.get((grid_x, grid_y))
                    if tile:
                        screen_x, screen_y = tile.get_screen_pos()
                        screen_x, screen_y = self.world_to_screen(screen_x, screen_y)
                        
                        points = [
                            (screen_x, screen_y + self.grid.tile_height/2 * self.camera.zoom),
                            (screen_x + self.grid.tile_width/2 * self.camera.zoom, screen_y),
                            (screen_x, screen_y - self.grid.tile_height/2 * self.camera.zoom),
                            (screen_x - self.grid.tile_width/2 * self.camera.zoom, screen_y)
                        ]
                        pygame.draw.polygon(surface, (255, 100, 100, 128), points, max(1, int(2 * self.camera.zoom)))
    
    def init_grid(self):
        """Grid'i başlangıç durumuna getirir"""
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[(x, y)] = Tile(x, y, self.grid)
    
    def init_characters(self):
        """Test karakterlerini oluşturur"""
        from ..entities.character_classes import Warrior, Archer, Healer, Mage
        
        # Oyuncu karakterleri
        warrior = Character("Savaşçı", 1, 1, self.grid, self, Warrior())
        warrior.color = (50, 150, 250)  # Mavi
        self.add_character(warrior)
        
        archer = Character("Okçu", 1, 2, self.grid, self, Archer())
        archer.color = (50, 200, 50)  # Yeşil
        self.add_character(archer)
        
        healer = Character("İyileştirici", 2, 1, self.grid, self, Healer())
        healer.color = (200, 200, 50)  # Sarı
        self.add_character(healer)
        
        # Düşman karakterleri
        enemy_mage = Character("Kara Büyücü", 8, 8, self.grid, self, Mage())
        enemy_mage.color = (250, 50, 50)  # Kırmızı
        self.add_character(enemy_mage)
        
        enemy_warrior = Character("Karanlık Şövalye", 8, 7, self.grid, self, Warrior())
        enemy_warrior.color = (200, 50, 200)  # Mor
        self.add_character(enemy_warrior)
    
    def add_character(self, character: Character):
        """Sahneye karakter ekler"""
        self.characters.append(character)
        self.turn_manager.add_character(character)
        tile = self.tiles.get((character.grid_x, character.grid_y))
        if tile:
            tile.occupied = True
    
    def get_character_at(self, grid_x: int, grid_y: int) -> Optional[Character]:
        """Belirtilen grid pozisyonundaki karakteri döndürür"""
        for char in self.characters:
            if char.grid_x == grid_x and char.grid_y == grid_y:
                return char
        return None
    
    def remove_character(self, character: Character):
        """Karakteri sahneden kaldırır"""
        if character in self.characters:
            self.characters.remove(character)
            self.turn_manager.remove_character(character)
            tile = self.tiles.get((character.grid_x, character.grid_y))
            if tile:
                tile.occupied = False
            if character == self.selected_character:
                self.selected_character = None 