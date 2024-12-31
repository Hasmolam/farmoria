"""
Oyun karakterlerini temsil eden sınıf.
"""

import pygame
import math
from typing import Tuple, List, Optional, Dict
from engine.core import GameObject
from ..core.grid import IsometricGrid, Tile
from .character_classes import CharacterClass, Skill, SkillType

class Character(GameObject):
    """Oynanabilir karakter sınıfı"""
    def __init__(self, name: str, grid_x: int, grid_y: int, grid: IsometricGrid, scene=None, char_class: Optional[CharacterClass] = None):
        super().__init__()
        self.name = name
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid = grid
        self.scene = scene
        
        # Karakter sınıfı ve özellikleri
        self.char_class = char_class or CharacterClass()
        self.max_hp = self.char_class.max_hp
        self.hp = self.max_hp
        self.attack_power = self.char_class.attack_power
        self.defense = self.char_class.defense
        self.movement = self.char_class.movement
        self.attack_range = self.char_class.attack_range
        self.skills = self.char_class.skills
        
        # Durum değişkenleri
        self.selected = False
        self.moved_this_turn = False
        self.attacked_this_turn = False
        self.used_skill_this_turn = False
        
        # Geçici etkiler
        self.buffs: Dict[str, int] = {}  # {etki_adı: kalan_tur}
        
        # Görsel özellikler
        self.color = (200, 50, 50)  # Kırmızı
        self.size = 20
        self.direction = 0  # Yön (derece cinsinden)
        
    def get_screen_pos(self) -> Tuple[float, float]:
        """Karakterin ekran pozisyonunu hesaplar"""
        return self.grid.cart_to_iso(self.grid_x, self.grid_y)
    
    def can_move_to(self, tile: Tile) -> bool:
        """Belirtilen kareye hareket edilebilir mi kontrol eder"""
        if self.moved_this_turn:
            return False
            
        dx = abs(tile.grid_x - self.grid_x)
        dy = abs(tile.grid_y - self.grid_y)
        distance = dx + dy
        
        return (distance <= self.movement and 
                tile.walkable and 
                not tile.occupied)
    
    def move_to(self, tile: Tile):
        """Karakteri belirtilen kareye hareket ettirir"""
        if self.can_move_to(tile):
            # Eski pozisyonu boşalt
            current_tile = self.get_current_tile()
            if current_tile:
                current_tile.occupied = False
            
            # Yeni pozisyona geç
            old_x, old_y = self.grid_x, self.grid_y
            self.grid_x = tile.grid_x
            self.grid_y = tile.grid_y
            tile.occupied = True
            self.moved_this_turn = True
            
            # Yönü güncelle
            dx = self.grid_x - old_x
            dy = self.grid_y - old_y
            if dx != 0 or dy != 0:
                self.direction = math.degrees(math.atan2(dy, dx))
    
    def can_attack(self, target: 'Character') -> bool:
        """Hedef karaktere saldırabilir mi kontrol eder"""
        if self.attacked_this_turn:
            return False
            
        dx = abs(target.grid_x - self.grid_x)
        dy = abs(target.grid_y - self.grid_y)
        distance = dx + dy
        
        return distance <= self.attack_range
    
    def attack(self, target: 'Character'):
        """Hedef karaktere saldırır"""
        if self.can_attack(target):
            damage = max(0, self.attack_power - target.defense)
            target.take_damage(damage)
            self.attacked_this_turn = True
    
    def take_damage(self, damage: int):
        """Hasar alır"""
        self.hp = max(0, self.hp - damage)
    
    def heal(self, amount: int):
        """Can yeniler"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def can_use_skill(self, skill: Skill, target_pos: Tuple[int, int]) -> bool:
        """Yeteneği kullanabilir mi kontrol eder"""
        if self.used_skill_this_turn or skill.current_cooldown > 0:
            return False
            
        dx = abs(target_pos[0] - self.grid_x)
        dy = abs(target_pos[1] - self.grid_y)
        distance = dx + dy
        
        return distance <= skill.range
    
    def use_skill(self, skill: Skill, target_pos: Tuple[int, int]):
        """Yeteneği kullanır"""
        if not self.can_use_skill(skill, target_pos):
            return
            
        # Hedef karakteri veya karakterleri bul
        targets = []
        if skill.area_effect:
            # Alan etkisi için tüm komşu karelerdeki karakterleri bul
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                    if target := self.scene.get_character_at(*check_pos):
                        targets.append(target)
        else:
            # Tek hedef için sadece tıklanan karedeki karakteri al
            if target := self.scene.get_character_at(*target_pos):
                targets.append(target)
        
        # Yeteneği uygula
        for target in targets:
            if skill.type == SkillType.ATTACK:
                # Saldırı yetenekleri için karakter saldırı gücünün yarısı eklenir
                damage = max(0, skill.damage + self.attack_power//2 - target.defense)
                target.take_damage(damage)
            
            elif skill.type == SkillType.HEAL:
                target.heal(skill.healing)
            
            elif skill.type == SkillType.BUFF:
                # Güçlendirme etkisi
                if "defense_up" in skill.description.lower():
                    target.buffs["defense_up"] = 2
                    target.defense += skill.effect_power
                elif "saldırı" in skill.description.lower():
                    target.buffs["attack_up"] = 2
                    target.attack_power += skill.effect_power
            
            elif skill.type == SkillType.DEBUFF:
                # Zayıflatma etkisi
                if "savunma" in skill.description.lower():
                    target.buffs["defense_down"] = 2
                    target.defense -= skill.effect_power
                elif "saldırı" in skill.description.lower():
                    target.buffs["attack_down"] = 2
                    target.attack_power -= skill.effect_power
        
        skill.current_cooldown = skill.cooldown
        self.used_skill_this_turn = True
    
    def update_buffs(self):
        """Geçici etkileri günceller"""
        buffs_to_remove = []
        for buff_name, turns_left in self.buffs.items():
            self.buffs[buff_name] = turns_left - 1
            if self.buffs[buff_name] <= 0:
                buffs_to_remove.append(buff_name)
                # Etkiyi kaldır
                if buff_name == "defense_up":
                    self.defense -= 8  # Savaşçının savunma artışı
                elif buff_name == "defense_down":
                    self.defense += 6  # Büyücünün savunma azaltması
                elif buff_name == "attack_up":
                    self.attack_power -= 10  # Okçunun saldırı artışı
                elif buff_name == "attack_down":
                    self.attack_power += 8  # Genel saldırı azaltması
                    
        for buff_name in buffs_to_remove:
            del self.buffs[buff_name]
    
    def get_current_tile(self) -> Optional[Tile]:
        """Karakterin bulunduğu kareyi döndürür"""
        if self.scene:
            return self.scene.tiles.get((self.grid_x, self.grid_y))
        return None
    
    def end_turn(self):
        """Turu sonlandırır"""
        self.moved_this_turn = False
        self.attacked_this_turn = False
        self.used_skill_this_turn = False
        # Yetenek bekleme sürelerini güncelle
        for skill in self.skills:
            if skill.current_cooldown > 0:
                skill.current_cooldown -= 1
        # Geçici etkileri güncelle
        self.update_buffs() 