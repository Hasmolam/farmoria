"""
Yapay zeka kontrolcüsü.
"""

from typing import List, Tuple, Optional, Dict
from ..entities.character import Character
from ..core.game_mode import TeamType
import math
import time
import random

class AIPersonality:
    """AI kişilik özellikleri"""
    def __init__(self):
        # Rastgele kişilik özellikleri
        self.aggression = random.uniform(0.5, 1.5)     # Saldırganlık çarpanı
        self.caution = random.uniform(0.5, 1.5)        # İhtiyatlılık çarpanı
        self.skill_preference = random.uniform(0.8, 1.2)  # Yetenek kullanma eğilimi
        
        # Tercih edilen hedef tipleri (rastgele sırala)
        self.target_priorities = list(range(3))  # 0: Düşük can, 1: İyileştirici, 2: En yakın
        random.shuffle(self.target_priorities)
        
        # Rastgele hareket tercihleri
        self.prefers_distance = random.choice([True, False])  # Mesafeli durmayı tercih eder mi?
        self.position_randomness = random.uniform(0.1, 0.3)   # Konum seçimindeki rastgelelik

class AIDelay:
    """AI hareket gecikmesi"""
    MOVE_DELAY = 1.0      # Hareket gecikmesi (saniye)
    ATTACK_DELAY = 1.5    # Saldırı gecikmesi
    SKILL_DELAY = 2.0     # Yetenek gecikmesi
    PRE_ACTION_DELAY = 0.5  # Aksiyon öncesi bekleme
    
    def __init__(self):
        self.last_action_time = 0
        self.current_delay = 0
        self.pre_action_phase = True  # Aksiyon öncesi bekleme aşaması
    
    def set_delay(self, action_type: str):
        """Aksiyon tipine göre gecikme ayarlar"""
        self.last_action_time = time.time()
        self.pre_action_phase = True
        self.current_delay = self.PRE_ACTION_DELAY
        self.action_type = action_type  # Sonraki aşama için sakla
    
    def is_ready(self) -> bool:
        """Gecikme süresi doldu mu kontrol eder"""
        if time.time() - self.last_action_time >= self.current_delay:
            if self.pre_action_phase:
                # Pre-action aşaması bitti, ana aksiyona geç
                self.pre_action_phase = False
                self.last_action_time = time.time()
                if self.action_type == "move":
                    self.current_delay = self.MOVE_DELAY
                elif self.action_type == "attack":
                    self.current_delay = self.ATTACK_DELAY
                elif self.action_type == "skill":
                    self.current_delay = self.SKILL_DELAY
                return False
            return True
        return False

class AIAction:
    """Yapay zeka aksiyonu"""
    def __init__(self, action_type: str, target_pos: Tuple[int, int], 
                 target_char: Optional[Character] = None, skill_index: int = -1):
        self.action_type = action_type  # "move", "attack", "skill"
        self.target_pos = target_pos
        self.target_char = target_char
        self.skill_index = skill_index
        self.score = 0.0  # Aksiyonun değeri
        self.started = False  # Aksiyon başladı mı?

class AIController:
    """Yapay zeka kontrolcüsü"""
    def __init__(self, scene):
        self.scene = scene
        self.delay = AIDelay()
        self.current_action: Optional[AIAction] = None
        self.highlight_character = None  # Vurgulanan karakter
        self.personalities: Dict[Character, AIPersonality] = {}  # Karakter kişilikleri
    
    def get_personality(self, character: Character) -> AIPersonality:
        """Karakterin kişiliğini döndürür, yoksa yeni oluşturur"""
        if character not in self.personalities:
            self.personalities[character] = AIPersonality()
        return self.personalities[character]
    
    def update(self, character: Character) -> bool:
        """AI karakterini günceller, tur bitti mi döndürür"""
        # Mevcut aksiyon yoksa yeni aksiyon al
        if not self.current_action:
            self.current_action = self.get_best_action(character)
            if not self.current_action:
                return True  # Yapılacak aksiyon kalmadı
            self.delay.set_delay(self.current_action.action_type)
            self.highlight_character = character  # Karakteri vurgula
            character.selected = True  # Seçili olarak işaretle
            return False
        
        # Gecikme süresi dolmadıysa bekle
        if not self.delay.is_ready():
            # Pre-action aşamasında hedefi vurgula
            if self.delay.pre_action_phase and self.current_action.target_char:
                self.current_action.target_char.selected = True
            return False
        
        # Aksiyonu uygula
        if not self.current_action.started:
            self.current_action.started = True
            
            # Önceki vurgulamaları temizle
            if self.highlight_character:
                self.highlight_character.selected = False
            if self.current_action.target_char:
                self.current_action.target_char.selected = False
            
            if self.current_action.action_type == "move":
                tile = self.scene.tiles.get(self.current_action.target_pos)
                if tile:
                    character.move_to(tile)
            
            elif self.current_action.action_type == "attack":
                if self.current_action.target_char:
                    character.attack(self.current_action.target_char)
            
            elif self.current_action.action_type == "skill":
                if (self.current_action.skill_index >= 0 and 
                    self.current_action.skill_index < len(character.skills)):
                    skill = character.skills[self.current_action.skill_index]
                    character.use_skill(skill, self.current_action.target_pos)
        
        # Aksiyon tamamlandı, sıradakine geç
        self.current_action = None
        self.highlight_character = None
        
        # Tüm aksiyonlar bitti mi kontrol et
        if character.moved_this_turn and character.attacked_this_turn and character.used_skill_this_turn:
            character.selected = False  # Seçimi kaldır
            return True
        
        return False
    
    def get_best_action(self, character: Character) -> Optional[AIAction]:
        """Karakter için en iyi aksiyonu belirler"""
        possible_actions = self.get_possible_actions(character)
        if not possible_actions:
            return None
            
        # Her aksiyonu değerlendir
        for action in possible_actions:
            self.evaluate_action(action, character)
        
        # En iyi aksiyonları filtrele
        max_score = max(action.score for action in possible_actions)
        best_actions = [action for action in possible_actions 
                       if action.score >= max_score * 0.9]  # En iyiye yakın olanları al
        
        # Rastgele birini seç
        return random.choice(best_actions)
    
    def get_possible_actions(self, character: Character) -> List[AIAction]:
        """Karakterin yapabileceği tüm aksiyonları listeler"""
        actions = []
        
        # Hareket aksiyonları
        if not character.moved_this_turn:
            for dx in range(-character.movement, character.movement + 1):
                for dy in range(-character.movement, character.movement + 1):
                    if abs(dx) + abs(dy) <= character.movement:
                        new_x = character.grid_x + dx
                        new_y = character.grid_y + dy
                        tile = self.scene.tiles.get((new_x, new_y))
                        if tile and tile.walkable and not tile.occupied:
                            actions.append(AIAction("move", (new_x, new_y)))
        
        # Saldırı aksiyonları
        if not character.attacked_this_turn:
            for target in self.scene.characters:
                if self.scene.game_mode.get_team(target) == TeamType.PLAYER:
                    dx = abs(target.grid_x - character.grid_x)
                    dy = abs(target.grid_y - character.grid_y)
                    if dx + dy <= character.attack_range:
                        actions.append(AIAction("attack", (target.grid_x, target.grid_y), target))
        
        # Yetenek aksiyonları
        if not character.used_skill_this_turn:
            for i, skill in enumerate(character.skills):
                if skill.current_cooldown == 0:
                    # Saldırı yetenekleri
                    if skill.type == "ATTACK":
                        for target in self.scene.characters:
                            if self.scene.game_mode.get_team(target) == TeamType.PLAYER:
                                dx = abs(target.grid_x - character.grid_x)
                                dy = abs(target.grid_y - character.grid_y)
                                if dx + dy <= skill.range:
                                    actions.append(AIAction("skill", (target.grid_x, target.grid_y), 
                                                         target, i))
                    
                    # İyileştirme yetenekleri
                    elif skill.type == "HEAL":
                        for ally in self.scene.characters:
                            if (self.scene.game_mode.get_team(ally) == TeamType.ENEMY and 
                                ally.hp < ally.max_hp):
                                dx = abs(ally.grid_x - character.grid_x)
                                dy = abs(ally.grid_y - character.grid_y)
                                if dx + dy <= skill.range:
                                    actions.append(AIAction("skill", (ally.grid_x, ally.grid_y), 
                                                         ally, i))
        
        return actions
    
    def evaluate_action(self, action: AIAction, character: Character):
        """Aksiyonun değerini hesaplar"""
        score = 0.0
        personality = self.get_personality(character)
        
        if action.action_type == "move":
            # Hareket değerlendirmesi
            # En yakın düşmana göre pozisyon
            nearest_enemy = self.find_nearest_enemy(character)
            if nearest_enemy:
                current_dist = self.manhattan_distance(character.grid_x, character.grid_y,
                                                    nearest_enemy.grid_x, nearest_enemy.grid_y)
                new_dist = self.manhattan_distance(action.target_pos[0], action.target_pos[1],
                                                 nearest_enemy.grid_x, nearest_enemy.grid_y)
                
                # Kişiliğe göre mesafe tercihi
                if personality.prefers_distance:
                    # Mesafeli durmayı tercih eder
                    optimal_distance = character.attack_range
                    score += (abs(new_dist - optimal_distance) - abs(current_dist - optimal_distance)) * 10
                else:
                    # Yakın dövüşü tercih eder
                    score += (current_dist - new_dist) * 10 * personality.aggression
                
                # Menzil içine girme bonusu
                if new_dist <= character.attack_range:
                    score += 30 * personality.aggression
            
            # Rastgele konum tercihi
            score += random.uniform(-20, 20) * personality.position_randomness
        
        elif action.action_type == "attack":
            # Saldırı değerlendirmesi
            target = action.target_char
            if target:
                # Hedef önceliklerine göre puan
                for i, priority in enumerate(personality.target_priorities):
                    if priority == 0 and target.hp < target.max_hp * 0.5:  # Düşük can
                        score += (100 - i * 20) * personality.aggression
                    elif priority == 1 and target.name == "İyileştirici":  # İyileştirici
                        score += (100 - i * 20) * personality.aggression
                    elif priority == 2:  # En yakın hedef
                        dist = self.manhattan_distance(character.grid_x, character.grid_y,
                                                    target.grid_x, target.grid_y)
                        score += (50 - dist * 5 - i * 20) * personality.aggression
                
                # Vereceğimiz hasar
                damage = max(0, character.attack_power - target.defense)
                score += damage * 2 * personality.aggression
                
                # Rastgele hedef tercihi
                score += random.uniform(-10, 10)
        
        elif action.action_type == "skill":
            # Yetenek değerlendirmesi
            skill = character.skills[action.skill_index]
            target = action.target_char
            
            # Yetenek kullanma eğilimi
            score += 20 * personality.skill_preference
            
            if skill.type == "ATTACK":
                # Saldırı yeteneği
                if target:
                    # Hedef önceliklerine göre puan
                    for i, priority in enumerate(personality.target_priorities):
                        if priority == 0 and target.hp < target.max_hp * 0.5:  # Düşük can
                            score += (120 - i * 20) * personality.aggression
                        elif priority == 1 and target.name == "İyileştirici":  # İyileştirici
                            score += (120 - i * 20) * personality.aggression
                    
                    # Alan hasarı bonusu
                    if skill.area_effect:
                        nearby_enemies = self.count_nearby_enemies(target.grid_x, target.grid_y)
                        score += nearby_enemies * 30 * personality.aggression
                    
                    # Hasar hesabı
                    damage = max(0, skill.damage + character.attack_power//2 - target.defense)
                    score += damage * 3 * personality.aggression
            
            elif skill.type == "HEAL":
                # İyileştirme yeteneği
                if target:
                    # Can eksikliği
                    missing_hp = target.max_hp - target.hp
                    score += min(missing_hp, skill.healing) * 2 * personality.caution
                    
                    # Alan etkisi bonusu
                    if skill.area_effect:
                        nearby_allies = self.count_nearby_allies(target.grid_x, target.grid_y)
                        score += nearby_allies * 20 * personality.caution
            
            # Rastgele yetenek tercihi
            score += random.uniform(-15, 15)
        
        action.score = score
    
    def manhattan_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """İki nokta arasındaki Manhattan mesafesini hesaplar"""
        return abs(x2 - x1) + abs(y2 - y1)
    
    def find_nearest_enemy(self, character: Character) -> Optional[Character]:
        """En yakın düşmanı bulur"""
        nearest_dist = float('inf')
        nearest_enemy = None
        
        for target in self.scene.characters:
            if self.scene.game_mode.get_team(target) == TeamType.PLAYER:
                dist = self.manhattan_distance(character.grid_x, character.grid_y,
                                            target.grid_x, target.grid_y)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_enemy = target
        
        return nearest_enemy
    
    def count_nearby_enemies(self, grid_x: int, grid_y: int) -> int:
        """Belirtilen konumun etrafındaki düşman sayısını sayar"""
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                char = self.scene.get_character_at(grid_x + dx, grid_y + dy)
                if char and self.scene.game_mode.get_team(char) == TeamType.PLAYER:
                    count += 1
        return count
    
    def count_nearby_allies(self, grid_x: int, grid_y: int) -> int:
        """Belirtilen konumun etrafındaki müttefik sayısını sayar"""
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                char = self.scene.get_character_at(grid_x + dx, grid_y + dy)
                if char and self.scene.game_mode.get_team(char) == TeamType.ENEMY:
                    count += 1
        return count 