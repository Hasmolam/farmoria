import json
from typing import Dict, Any, Optional
import os
import pygame
from ..utils.data_manager import DataManager
from .base import GameObject, GameSystem

class GameState:
    """Oyun durumunu yöneten sınıf"""
    def __init__(self):
        self.data = {}
        self.data_manager = DataManager()
        
    def set(self, key: str, value: Any):
        """Duruma veri ekler"""
        self.data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Durumdan veri alır"""
        return self.data.get(key, default)
        
    def remove(self, key: str):
        """Durumdan veri siler"""
        if key in self.data:
            del self.data[key]
            
    def clear(self):
        """Tüm durumu temizler"""
        self.data.clear()
        
    def save(self, filename: str):
        """Durumu dosyaya kaydeder"""
        self.data_manager.save_json(filename, self.data)
        
    def load(self, filename: str):
        """Durumu dosyadan yükler"""
        data = self.data_manager.load_json(filename)
        if data:
            self.data = data

class GameStateManager(GameSystem):
    """Oyun durumlarını yöneten sistem"""
    def __init__(self):
        super().__init__("GameStateManager")
        self.states: Dict[str, GameState] = {}
        self.active_state: Optional[str] = None
        
    def create_state(self, name: str) -> GameState:
        """Yeni bir durum oluşturur"""
        state = GameState()
        self.states[name] = state
        return state
        
    def get_state(self, name: str) -> Optional[GameState]:
        """İsme göre durumu döndürür"""
        return self.states.get(name)
        
    def set_active_state(self, name: str):
        """Aktif durumu değiştirir"""
        if name in self.states:
            self.active_state = name
            
    def get_active_state(self) -> Optional[GameState]:
        """Aktif durumu döndürür"""
        if self.active_state:
            return self.states.get(self.active_state)
        return None
        
    def remove_state(self, name: str):
        """Durumu siler"""
        if name in self.states:
            del self.states[name]
            if self.active_state == name:
                self.active_state = None
                
    def clear_states(self):
        """Tüm durumları temizler"""
        self.states.clear()
        self.active_state = None
        
    def save_state(self, name: str, filename: str):
        """Durumu dosyaya kaydeder"""
        state = self.get_state(name)
        if state:
            state.save(filename)
            
    def load_state(self, name: str, filename: str):
        """Durumu dosyadan yükler"""
        state = self.get_state(name)
        if state:
            state.load(filename)
            
    def save_all_states(self, directory: str):
        """Tüm durumları kaydeder"""
        os.makedirs(directory, exist_ok=True)
        for name, state in self.states.items():
            filename = os.path.join(directory, f"{name}.json")
            state.save(filename)
            
    def load_all_states(self, directory: str):
        """Tüm durumları yükler"""
        if not os.path.exists(directory):
            return
            
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                name = os.path.splitext(filename)[0]
                state = self.create_state(name)
                state.load(os.path.join(directory, filename)) 