"""
Oyun modu ve akış yönetimi.
"""

from enum import Enum, auto
from typing import List, Optional, Dict
from ..entities.character import Character

class TeamType(Enum):
    """Takım türleri"""
    PLAYER = auto()
    ENEMY = auto()

class GameState(Enum):
    """Oyun durumları"""
    SETUP = auto()      # Oyun başlangıcı
    PLAYING = auto()    # Oyun devam ediyor
    VICTORY = auto()    # Oyuncu kazandı
    DEFEAT = auto()     # Oyuncu kaybetti
    PAUSED = auto()     # Oyun duraklatıldı

class BattleObjective:
    """Savaş hedefi"""
    def __init__(self, description: str):
        self.description = description
        self.completed = False

class GameMode:
    """Oyun modu yöneticisi"""
    def __init__(self):
        self.state = GameState.SETUP
        self.teams: Dict[TeamType, List[Character]] = {
            TeamType.PLAYER: [],
            TeamType.ENEMY: []
        }
        self.current_turn = 1
        self.objectives: List[BattleObjective] = []
        self.setup_battle()
    
    def setup_battle(self):
        """Savaş hedeflerini ve kurallarını ayarlar"""
        # Ana hedef: Tüm düşmanları yenmek
        self.objectives.append(BattleObjective("Tüm düşmanları yen"))
        
        # Bonus hedefler
        self.objectives.append(BattleObjective("İyileştiriciyi hayatta tut"))
        self.objectives.append(BattleObjective("Savaşı 10 turdan önce bitir"))
    
    def add_character(self, character: Character, team: TeamType):
        """Karakteri belirtilen takıma ekler"""
        self.teams[team].append(character)
    
    def check_game_over(self) -> Optional[GameState]:
        """Oyunun bitip bitmediğini kontrol eder"""
        # Tüm düşmanlar öldü mü?
        if not self.teams[TeamType.ENEMY]:
            self.objectives[0].completed = True  # Ana hedef tamamlandı
            if self.current_turn <= 10:
                self.objectives[2].completed = True  # Hızlı zafer hedefi
            return GameState.VICTORY
        
        # Tüm oyuncular öldü mü?
        if not self.teams[TeamType.PLAYER]:
            return GameState.DEFEAT
        
        # İyileştirici hayatta mı?
        healer_alive = any(char.name == "İyileştirici" for char in self.teams[TeamType.PLAYER])
        if healer_alive:
            self.objectives[1].completed = True
        
        return None
    
    def next_turn(self):
        """Sonraki tura geçer"""
        self.current_turn += 1
    
    def get_team(self, character: Character) -> Optional[TeamType]:
        """Karakterin hangi takımda olduğunu döndürür"""
        for team_type, team in self.teams.items():
            if character in team:
                return team_type
        return None
    
    def remove_character(self, character: Character):
        """Ölen karakteri oyundan kaldırır"""
        team = self.get_team(character)
        if team:
            self.teams[team].remove(character)
    
    def get_battle_status(self) -> str:
        """Mevcut savaş durumunu döndürür"""
        status = f"Tur: {self.current_turn}\n\n"
        status += "Hedefler:\n"
        
        for i, objective in enumerate(self.objectives):
            check = "✓" if objective.completed else "✗"
            status += f"{check} {objective.description}\n"
        
        status += f"\nOyuncu Takımı: {len(self.teams[TeamType.PLAYER])} karakter\n"
        status += f"Düşman Takımı: {len(self.teams[TeamType.ENEMY])} karakter"
        
        return status 