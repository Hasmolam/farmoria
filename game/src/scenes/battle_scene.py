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
from ..core.game_mode import GameMode, TeamType, GameState, BattleObjective
from ..ui.battle_ui import BattleUI, UIColors
from ..ai.ai_controller import AIController
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
        self.game_mode = GameMode()
        self.ai_controller = AIController(self)
        
        # Grid'i ekranın ortasına yerleştirmek için offset
        self.offset_x = 400 - (width * self.grid.tile_width/4)
        self.offset_y = 300 - (height * self.grid.tile_height/4)
        
        # Kamera sistemi
        self.camera = Camera(800, 600)  # Ekran boyutları
        
        # UI sistemi
        self.ui = BattleUI(800, 600)
        
        self.init_grid()
        self.init_characters()
        
        # Oyunu başlat
        self.game_mode.state = GameState.PLAYING
    
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
        if self.game_mode.state != GameState.PLAYING:
            return
            
        # Kamera kontrollerini işle
        self.camera.handle_input(events)
        
        # Mevcut karakter
        current_char = self.turn_manager.get_current_character()
        if not current_char:
            return
            
        # Eğer AI kontrolündeki karakter ise
        if self.game_mode.get_team(current_char) == TeamType.ENEMY:
            # AI aksiyonlarını güncelle
            if self.ai_controller.update(current_char):
                # AI turu bitti
                next_char = self.turn_manager.next_turn()
                self.game_mode.next_turn()
                if next_char:
                    self.selected_character = next_char
                    next_char.selected = True
            return
        
        # Oyuncu kontrolündeki karakter için normal güncelleme
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.screen_to_world(*mouse_pos)
        grid_pos = self.grid.iso_to_cart(*world_pos)
        
        # Tuş kontrolleri
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Boşluk tuşu ile turu bitir
                    if self.turn_manager.can_end_turn():
                        next_char = self.turn_manager.next_turn()
                        self.game_mode.next_turn()
                        if next_char:
                            self.selected_character = next_char
                            next_char.selected = True
                
                # Yetenek tuşları (1-4)
                if self.selected_character and self.selected_character == current_char:
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
                
                if clicked_char:
                    if self.selected_character and self.selected_character == current_char:
                        if clicked_char != current_char:
                            # Saldırı kontrolü
                            if self.selected_character.can_attack(clicked_char):
                                self.selected_character.attack(clicked_char)
                                if clicked_char.hp <= 0:
                                    # Karakter öldü
                                    self.remove_character(clicked_char)
                                    # Oyun durumunu kontrol et
                                    if game_state := self.game_mode.check_game_over():
                                        self.game_mode.state = game_state
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
        # Arka plan
        surface.fill(UIColors.BACKGROUND)
        
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
            pygame.draw.polygon(surface, UIColors.TEXT_DARK, points, 1)
            
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
            pygame.draw.line(surface, UIColors.TEXT_DARK, (screen_x, screen_y), (end_x, end_y), 
                           max(1, int(3 * self.camera.zoom)))
            
            # Seçili durumu
            if character.selected:
                pygame.draw.circle(surface, UIColors.SELECTED, (int(screen_x), int(screen_y)), 
                                 int(size + 4 * self.camera.zoom), max(1, int(2 * self.camera.zoom)))
                
            # HP göstergesi
            hp_width = 40 * self.camera.zoom
            hp_height = 4 * self.camera.zoom
            hp_x = screen_x - hp_width/2
            hp_y = screen_y - size - 10 * self.camera.zoom
            
            # HP arkaplan
            pygame.draw.rect(surface, UIColors.DANGER, 
                            (hp_x, hp_y, hp_width, hp_height))
            
            # Mevcut HP
            current_width = (character.hp / character.max_hp) * hp_width
            pygame.draw.rect(surface, UIColors.SUCCESS, 
                            (hp_x, hp_y, current_width, hp_height))
            
            # Karakter ismi
            name_surface = pygame.font.SysFont('Arial', int(24 * self.camera.zoom)).render(
                character.name, True, UIColors.TEXT)
            name_rect = name_surface.get_rect(centerx=screen_x, bottom=screen_y - size - 15 * self.camera.zoom)
            surface.blit(name_surface, name_rect)
        
        # UI'ı render et
        self.ui.render(surface, self.selected_character, self.game_mode.objectives, self.game_mode.current_turn)
        
        # Oyun sonu mesajı
        if self.game_mode.state == GameState.VICTORY:
            self.render_game_over(surface, "Zafer! Tüm hedefler:", self.game_mode.objectives)
        elif self.game_mode.state == GameState.DEFEAT:
            self.render_game_over(surface, "Yenilgi!", [])
    
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
                        # Yarı saydam mavi
                        move_color = (*UIColors.PRIMARY, 128)
                        pygame.draw.polygon(surface, move_color, points)
                        pygame.draw.polygon(surface, UIColors.PRIMARY, points, 2)
    
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
                        # Yarı saydam kırmızı
                        attack_color = (*UIColors.DANGER, 128)
                        pygame.draw.polygon(surface, attack_color, points)
                        pygame.draw.polygon(surface, UIColors.DANGER, points, 2)
    
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
        self.add_character(warrior, TeamType.PLAYER)
        
        archer = Character("Okçu", 1, 2, self.grid, self, Archer())
        archer.color = (50, 200, 50)  # Yeşil
        self.add_character(archer, TeamType.PLAYER)
        
        healer = Character("İyileştirici", 2, 1, self.grid, self, Healer())
        healer.color = (200, 200, 50)  # Sarı
        self.add_character(healer, TeamType.PLAYER)
        
        # Düşman karakterleri
        enemy_mage = Character("Kara Büyücü", 8, 8, self.grid, self, Mage())
        enemy_mage.color = (250, 50, 50)  # Kırmızı
        self.add_character(enemy_mage, TeamType.ENEMY)
        
        enemy_warrior = Character("Karanlık Şövalye", 8, 7, self.grid, self, Warrior())
        enemy_warrior.color = (200, 50, 200)  # Mor
        self.add_character(enemy_warrior, TeamType.ENEMY)
    
    def add_character(self, character: Character, team: TeamType):
        """Sahneye karakter ekler"""
        self.characters.append(character)
        self.turn_manager.add_character(character)
        self.game_mode.add_character(character, team)
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
            self.game_mode.remove_character(character)
            tile = self.tiles.get((character.grid_x, character.grid_y))
            if tile:
                tile.occupied = False
            if character == self.selected_character:
                self.selected_character = None
    
    def render_game_over(self, surface: pygame.Surface, title: str, objectives: List[BattleObjective]):
        """Oyun sonu ekranını render eder"""
        # Yarı saydam siyah arka plan
        overlay = pygame.Surface(surface.get_size())
        overlay.fill(UIColors.BACKGROUND)
        overlay.set_alpha(192)
        surface.blit(overlay, (0, 0))
        
        # Panel
        panel_width = 400
        panel_height = 300
        panel_x = surface.get_width()//2 - panel_width//2
        panel_y = surface.get_height()//2 - panel_height//2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, UIColors.PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(surface, UIColors.TEXT_DARK, panel_rect, width=2, border_radius=8)
        
        # Başlık
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        title_surface = title_font.render(title, True, UIColors.TEXT)
        title_rect = title_surface.get_rect(centerx=panel_x + panel_width//2, top=panel_y + 20)
        surface.blit(title_surface, title_rect)
        
        # Hedefler
        y_offset = panel_y + 80
        font = pygame.font.SysFont('Arial', 24)
        
        for objective in objectives:
            # Hedef kutusu
            obj_rect = pygame.Rect(panel_x + 20, y_offset, panel_width - 40, 40)
            pygame.draw.rect(surface, UIColors.BACKGROUND, obj_rect, border_radius=4)
            
            # Tamamlanma durumu
            check = "[+]" if objective.completed else "[ ]"
            check_color = UIColors.SUCCESS if objective.completed else UIColors.DANGER
            check_surface = font.render(check, True, check_color)
            surface.blit(check_surface, (panel_x + 30, y_offset + 10))
            
            # Hedef açıklaması
            desc_surface = font.render(objective.description, True, UIColors.TEXT)
            surface.blit(desc_surface, (panel_x + 70, y_offset + 10))
            
            y_offset += 50
        
        # Devam etmek için mesaj
        if self.game_mode.state == GameState.VICTORY:
            continue_text = "Tebrikler! Oyunu kazandınız."
            continue_color = UIColors.SUCCESS
        else:
            continue_text = "Oyun bitti. Tekrar deneyin."
            continue_color = UIColors.DANGER
            
        continue_surface = font.render(continue_text, True, continue_color)
        continue_rect = continue_surface.get_rect(centerx=panel_x + panel_width//2, bottom=panel_y + panel_height - 20)
        surface.blit(continue_surface, continue_rect) 