from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
import json
from pathlib import Path
from .data_manager import DataManager

@dataclass
class PlayerState:
    """Oyuncu durumu için temel sınıf"""
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0})
    health: float = 100.0
    score: int = 0
    level: int = 1
    inventory: Dict[str, Any] = field(default_factory=dict)
    abilities: Dict[str, bool] = field(default_factory=dict)

@dataclass
class WorldState:
    """Oyun dünyası durumu için temel sınıf"""
    current_level: str = "level_1"
    time_elapsed: float = 0.0
    active_quests: Dict[str, Any] = field(default_factory=dict)
    completed_quests: Dict[str, Any] = field(default_factory=dict)
    environment_state: Dict[str, Any] = field(default_factory=dict)

class GameState:
    def __init__(self, data_manager: Optional[DataManager] = None):
        """
        Args:
            data_manager: Veri yönetimi için DataManager örneği
        """
        self.data_manager = data_manager or DataManager()
        self.player = PlayerState()
        self.world = WorldState()
        self._custom_data: Dict[str, Any] = {}

    def save_state(self, file_path: str) -> None:
        """Oyun durumunu kaydeder.
        
        Args:
            file_path: Kayıt dosyasının yolu
        """
        state_data = {
            "player": asdict(self.player),
            "world": asdict(self.world),
            "custom_data": self._custom_data
        }
        self.data_manager.save(state_data, file_path)

    def load_state(self, file_path: str) -> None:
        """Oyun durumunu yükler.
        
        Args:
            file_path: Kayıt dosyasının yolu
        """
        try:
            state_data = self.data_manager.load(file_path)
            self.player = PlayerState(**state_data["player"])
            self.world = WorldState(**state_data["world"])
            self._custom_data = state_data.get("custom_data", {})
        except Exception as e:
            raise ValueError(f"Oyun durumu yüklenirken hata: {e}")

    def set_custom_data(self, key: str, value: Any) -> None:
        """Özel veri ekler.
        
        Args:
            key: Veri anahtarı
            value: Veri değeri
        """
        self._custom_data[key] = value

    def get_custom_data(self, key: str, default: Any = None) -> Any:
        """Özel veriyi getirir.
        
        Args:
            key: Veri anahtarı
            default: Varsayılan değer
            
        Returns:
            Veri değeri
        """
        return self._custom_data.get(key, default)

    def update_player_position(self, x: float, y: float, z: float = 0.0) -> None:
        """Oyuncu pozisyonunu günceller.
        
        Args:
            x: X koordinatı
            y: Y koordinatı
            z: Z koordinatı (opsiyonel)
        """
        self.player.position = {"x": x, "y": y, "z": z}

    def add_to_score(self, points: int) -> None:
        """Skora puan ekler.
        
        Args:
            points: Eklenecek puan
        """
        self.player.score += points

    def set_level(self, level: int) -> None:
        """Oyuncu seviyesini ayarlar.
        
        Args:
            level: Yeni seviye
        """
        self.player.level = level

    def update_health(self, health: float) -> None:
        """Oyuncu sağlığını günceller.
        
        Args:
            health: Yeni sağlık değeri
        """
        self.player.health = max(0.0, min(100.0, health))

    def add_to_inventory(self, item_id: str, quantity: int = 1, **properties) -> None:
        """Envantere eşya ekler.
        
        Args:
            item_id: Eşya kimliği
            quantity: Miktar
            properties: Ek özellikler
        """
        if item_id not in self.player.inventory:
            self.player.inventory[item_id] = {
                "quantity": quantity,
                **properties
            }
        else:
            self.player.inventory[item_id]["quantity"] += quantity

    def remove_from_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Envanterden eşya çıkarır.
        
        Args:
            item_id: Eşya kimliği
            quantity: Miktar
            
        Returns:
            İşlem başarılı ise True
        """
        if item_id in self.player.inventory:
            current_quantity = self.player.inventory[item_id]["quantity"]
            if current_quantity >= quantity:
                self.player.inventory[item_id]["quantity"] -= quantity
                if self.player.inventory[item_id]["quantity"] <= 0:
                    del self.player.inventory[item_id]
                return True
        return False

    def add_ability(self, ability_id: str, enabled: bool = True) -> None:
        """Yetenek ekler veya günceller.
        
        Args:
            ability_id: Yetenek kimliği
            enabled: Yeteneğin durumu
        """
        self.player.abilities[ability_id] = enabled

    def has_ability(self, ability_id: str) -> bool:
        """Yetenek kontrolü yapar.
        
        Args:
            ability_id: Yetenek kimliği
            
        Returns:
            Yetenek varsa ve aktifse True
        """
        return self.player.abilities.get(ability_id, False)

    def update_world_time(self, elapsed: float) -> None:
        """Dünya zamanını günceller.
        
        Args:
            elapsed: Geçen süre
        """
        self.world.time_elapsed = elapsed

    def add_quest(self, quest_id: str, quest_data: Dict[str, Any]) -> None:
        """Görev ekler.
        
        Args:
            quest_id: Görev kimliği
            quest_data: Görev bilgileri
        """
        self.world.active_quests[quest_id] = quest_data

    def complete_quest(self, quest_id: str) -> None:
        """Görevi tamamlar.
        
        Args:
            quest_id: Görev kimliği
        """
        if quest_id in self.world.active_quests:
            self.world.completed_quests[quest_id] = self.world.active_quests.pop(quest_id) 