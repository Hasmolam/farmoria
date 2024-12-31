"""
Savaş arayüzü bileşenleri.
"""

import pygame
from typing import Dict, List, Tuple, Optional
from ..entities.character import Character
from ..core.game_mode import BattleObjective

class UIColors:
    """UI renk paleti"""
    BACKGROUND = (40, 44, 52)      # Koyu arka plan
    PANEL = (30, 33, 39)           # Panel arka planı
    TEXT = (220, 223, 228)         # Ana metin
    TEXT_DARK = (157, 165, 180)    # İkincil metin
    PRIMARY = (97, 175, 239)       # Vurgu rengi
    SUCCESS = (152, 195, 121)      # Başarı/Pozitif
    WARNING = (229, 192, 123)      # Uyarı
    DANGER = (224, 108, 117)       # Tehlike/Negatif
    SELECTED = (229, 192, 123)     # Seçili öğe

class UIPanel:
    """Temel UI panel sınıfı"""
    def __init__(self, x: int, y: int, width: int, height: int, padding: int = 10):
        self.rect = pygame.Rect(x, y, width, height)
        self.padding = padding
        self.background_color = UIColors.PANEL
        self.border_radius = 8
        
    def render(self, surface: pygame.Surface):
        """Panel arka planını çizer"""
        pygame.draw.rect(surface, self.background_color, self.rect, 
                        border_radius=self.border_radius)
        pygame.draw.rect(surface, UIColors.BACKGROUND, self.rect, 
                        width=1, border_radius=self.border_radius)

class CharacterPanel(UIPanel):
    """Karakter bilgi paneli"""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 20)
        self.font_small = pygame.font.SysFont('Arial', 16)
        
    def render(self, surface: pygame.Surface, character: Character):
        """Karakter bilgilerini render eder"""
        super().render(surface)
        
        if not character:
            return
            
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding
        
        # Karakter ismi
        name_surface = self.font_large.render(character.name, True, UIColors.TEXT)
        surface.blit(name_surface, (x, y))
        y += 30
        
        # HP çubuğu
        hp_width = self.rect.width - 2 * self.padding
        hp_height = 20
        hp_rect = pygame.Rect(x, y, hp_width, hp_height)
        
        # HP arkaplan
        pygame.draw.rect(surface, UIColors.DANGER, hp_rect, border_radius=4)
        
        # Mevcut HP
        current_width = int((character.hp / character.max_hp) * hp_width)
        if current_width > 0:
            current_rect = pygame.Rect(x, y, current_width, hp_height)
            pygame.draw.rect(surface, UIColors.SUCCESS, current_rect, border_radius=4)
        
        # HP değeri
        hp_text = f"{character.hp}/{character.max_hp} HP"
        hp_surface = self.font_small.render(hp_text, True, UIColors.TEXT)
        hp_rect = hp_surface.get_rect(center=(x + hp_width/2, y + hp_height/2))
        surface.blit(hp_surface, hp_rect)
        y += hp_height + 10
        
        # Özellikler
        stats = [
            ("Saldırı", character.attack_power),
            ("Savunma", character.defense),
            ("Hareket", character.movement),
            ("Menzil", character.attack_range)
        ]
        
        for stat_name, stat_value in stats:
            stat_text = f"{stat_name}: {stat_value}"
            stat_surface = self.font.render(stat_text, True, UIColors.TEXT)
            surface.blit(stat_surface, (x, y))
            y += 25
        
        # Yetenekler
        y += 10
        skill_title = self.font.render("Yetenekler (1-4)", True, UIColors.TEXT)
        surface.blit(skill_title, (x, y))
        y += 25
        
        for i, skill in enumerate(character.skills):
            # Yetenek kutusu
            skill_rect = pygame.Rect(x, y, hp_width, 50)
            pygame.draw.rect(surface, UIColors.BACKGROUND, skill_rect, border_radius=4)
            
            # Yetenek ismi
            skill_name = f"{i+1}. {skill.name}"
            name_surface = self.font.render(skill_name, True, 
                                          UIColors.TEXT_DARK if skill.current_cooldown > 0 else UIColors.TEXT)
            surface.blit(name_surface, (x + 5, y + 5))
            
            # Yetenek açıklaması
            desc_surface = self.font_small.render(skill.description, True, UIColors.TEXT_DARK)
            surface.blit(desc_surface, (x + 5, y + 25))
            
            # Bekleme süresi
            if skill.current_cooldown > 0:
                cd_text = f"Bekleme: {skill.current_cooldown}"
                cd_surface = self.font_small.render(cd_text, True, UIColors.DANGER)
                cd_rect = cd_surface.get_rect(right=x + hp_width - 5, centery=y + 25)
                surface.blit(cd_surface, cd_rect)
            
            y += 60

class ObjectivesPanel(UIPanel):
    """Hedefler paneli"""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.font = pygame.font.SysFont('Arial', 20)
        self.font_small = pygame.font.SysFont('Arial', 16)
        
    def render(self, surface: pygame.Surface, objectives: List[BattleObjective], turn: int):
        """Hedefleri render eder"""
        super().render(surface)
        
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding
        
        # Tur sayısı
        turn_text = f"Tur: {turn}"
        turn_surface = self.font.render(turn_text, True, UIColors.TEXT)
        surface.blit(turn_surface, (x, y))
        y += 30
        
        # Hedefler
        for objective in objectives:
            # Hedef kutusu
            obj_rect = pygame.Rect(x, y, self.rect.width - 2 * self.padding, 30)
            pygame.draw.rect(surface, UIColors.BACKGROUND, obj_rect, border_radius=4)
            
            # Tamamlanma durumu
            check = "[+]" if objective.completed else "[ ]"
            check_color = UIColors.SUCCESS if objective.completed else UIColors.DANGER
            check_surface = self.font.render(check, True, check_color)
            surface.blit(check_surface, (x + 5, y + 5))
            
            # Hedef açıklaması
            desc_surface = self.font_small.render(objective.description, True, UIColors.TEXT)
            surface.blit(desc_surface, (x + 35, y + 7))
            
            y += 35

class BattleUI:
    """Savaş arayüzü yöneticisi"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Sağ panel (karakter bilgileri)
        panel_width = 300
        self.character_panel = CharacterPanel(
            screen_width - panel_width - 10,
            10,
            panel_width,
            screen_height - 20
        )
        
        # Sol panel (hedefler)
        objectives_height = 200
        self.objectives_panel = ObjectivesPanel(
            10,
            10,
            panel_width,
            objectives_height
        )
    
    def render(self, surface: pygame.Surface, selected_character: Optional[Character], 
               objectives: List[BattleObjective], turn: int):
        """Tüm UI elemanlarını render eder"""
        # Karakter paneli
        if selected_character:
            self.character_panel.render(surface, selected_character)
        
        # Hedefler paneli
        self.objectives_panel.render(surface, objectives, turn) 