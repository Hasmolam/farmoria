"""
Karakter sınıfları ve yetenekleri.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto

class SkillType(Enum):
    """Yetenek türleri"""
    ATTACK = auto()  # Saldırı
    HEAL = auto()    # İyileştirme
    BUFF = auto()    # Güçlendirme
    DEBUFF = auto()  # Zayıflatma

@dataclass
class Skill:
    """Karakter yeteneği"""
    name: str
    type: SkillType
    damage: int = 0
    healing: int = 0
    range: int = 1
    cooldown: int = 0
    current_cooldown: int = 0
    description: str = ""
    area_effect: bool = False  # Alan etkisi var mı?
    effect_power: int = 0  # Güçlendirme/zayıflatma etkisinin gücü

class CharacterClass:
    """Temel karakter sınıfı özellikleri"""
    def __init__(self):
        self.max_hp = 100
        self.attack_power = 15
        self.defense = 10
        self.movement = 4
        self.attack_range = 1
        self.skills: List[Skill] = []

class Warrior(CharacterClass):
    """Savaşçı sınıfı"""
    def __init__(self):
        super().__init__()
        self.max_hp = 120
        self.attack_power = 20
        self.defense = 15
        self.movement = 3
        self.attack_range = 1
        self.skills = [
            Skill(
                name="Güçlü Vuruş",
                type=SkillType.ATTACK,
                damage=30,
                range=1,
                cooldown=2,
                description="Güçlü bir yakın mesafe saldırısı"
            ),
            Skill(
                name="Savunma Duruşu",
                type=SkillType.BUFF,
                cooldown=3,
                description="Savunmayı 2 tur boyunca artırır",
                effect_power=8  # Savunma artış miktarı
            )
        ]

class Archer(CharacterClass):
    """Okçu sınıfı"""
    def __init__(self):
        super().__init__()
        self.max_hp = 80
        self.attack_power = 15
        self.defense = 8
        self.movement = 4
        self.attack_range = 3
        self.skills = [
            Skill(
                name="Çoklu Ok",
                type=SkillType.ATTACK,
                damage=20,
                range=2,
                cooldown=2,
                description="Birden fazla düşmana ok atar",
                area_effect=True
            ),
            Skill(
                name="Keskin Nişancı",
                type=SkillType.BUFF,
                cooldown=3,
                description="Saldırı gücünü 2 tur artırır",
                effect_power=10  # Saldırı gücü artış miktarı
            )
        ]

class Healer(CharacterClass):
    """İyileştirici sınıfı"""
    def __init__(self):
        super().__init__()
        self.max_hp = 70
        self.attack_power = 8
        self.defense = 7
        self.movement = 3
        self.attack_range = 2
        self.skills = [
            Skill(
                name="İyileştirme",
                type=SkillType.HEAL,
                healing=30,
                range=2,
                cooldown=1,
                description="Bir müttefiki iyileştirir"
            ),
            Skill(
                name="Toplu İyileştirme",
                type=SkillType.HEAL,
                healing=15,
                range=3,
                cooldown=4,
                description="Tüm müttefikleri iyileştirir",
                area_effect=True
            )
        ]

class Mage(CharacterClass):
    """Büyücü sınıfı"""
    def __init__(self):
        super().__init__()
        self.max_hp = 60
        self.attack_power = 25
        self.defense = 5
        self.movement = 3
        self.attack_range = 4
        self.skills = [
            Skill(
                name="Ateş Topu",
                type=SkillType.ATTACK,
                damage=35,
                range=3,
                cooldown=2,
                description="Güçlü bir uzak mesafe saldırısı",
                area_effect=True
            ),
            Skill(
                name="Zayıflatma",
                type=SkillType.DEBUFF,
                range=3,
                cooldown=3,
                description="Düşmanın savunmasını azaltır",
                effect_power=6  # Savunma azaltma miktarı
            )
        ] 