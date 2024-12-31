"""
Sıra tabanlı savaş sistemi için tur yöneticisi.
"""

from typing import List, Optional
from ..entities.character import Character

class TurnManager:
    """Sıra yöneticisi"""
    def __init__(self):
        self.characters: List[Character] = []
        self.current_index = 0
        self.current_character: Optional[Character] = None
        
    def add_character(self, character: Character):
        """Karakteri sıra sistemine ekler"""
        self.characters.append(character)
        if len(self.characters) == 1:
            self.current_character = character
            
    def remove_character(self, character: Character):
        """Karakteri sıra sisteminden çıkarır"""
        if character in self.characters:
            index = self.characters.index(character)
            self.characters.remove(character)
            
            # Eğer silinen karakter mevcut karakterse
            if character == self.current_character:
                # Sıradaki karaktere geç
                if self.characters:
                    self.current_index = index % len(self.characters)
                    self.current_character = self.characters[self.current_index]
                else:
                    self.current_character = None
                    
    def next_turn(self) -> Optional[Character]:
        """Sıradaki karakterin turuna geçer"""
        if not self.characters:
            return None
            
        # Mevcut karakterin turunu bitir
        if self.current_character:
            self.current_character.end_turn()
            
        # Sıradaki karaktere geç
        self.current_index = (self.current_index + 1) % len(self.characters)
        self.current_character = self.characters[self.current_index]
        return self.current_character
    
    def get_current_character(self) -> Optional[Character]:
        """Mevcut karakteri döndürür"""
        return self.current_character
    
    def can_end_turn(self) -> bool:
        """Mevcut karakterin turunu bitirip bitiremeyeceğini kontrol eder"""
        if not self.current_character:
            return False
        return self.current_character.moved_this_turn or self.current_character.attacked_this_turn 