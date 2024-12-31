from typing import Dict, Any, Optional
import pygame

class GameObject:
    """Oyun nesnelerinin temel sınıfı."""
    
    def __init__(self, name: str = "GameObject"):
        self.name = name
        self.components: Dict[str, Any] = {}
        self.enabled = True
        
    def add_component(self, component_name: str, component: Any) -> None:
        """Nesneye yeni bir bileşen ekler."""
        self.components[component_name] = component
        
    def get_component(self, component_name: str) -> Optional[Any]:
        """Belirtilen isimde bir bileşeni döndürür."""
        return self.components.get(component_name)
        
    def update(self, delta_time: float) -> None:
        """Nesneyi günceller."""
        if not self.enabled:
            return
            
        for component in self.components.values():
            if hasattr(component, 'update'):
                component.update(delta_time)
                
    def draw(self, surface: pygame.Surface) -> None:
        """Nesneyi çizer."""
        if not self.enabled:
            return
            
        for component in self.components.values():
            if hasattr(component, 'draw'):
                component.draw(surface)

class GameSystem:
    """Oyun sistemlerinin temel sınıfı."""
    
    def __init__(self, name: str = "GameSystem"):
        self.name = name
        self.enabled = True
        
    def initialize(self) -> None:
        """Sistemi başlatır."""
        pass
        
    def update(self, delta_time: float) -> None:
        """Sistemi günceller."""
        if not self.enabled:
            return
            
    def draw(self, surface: pygame.Surface) -> None:
        """Sistemi çizer."""
        if not self.enabled:
            return
            
    def cleanup(self) -> None:
        """Sistemi temizler."""
        pass 