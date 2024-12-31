import pytest
import pygame
from engine.core.base import GameObject, GameSystem

class TestGameObject:
    """GameObject sınıfı testleri"""
    
    @pytest.fixture
    def game_object(self):
        """Test için GameObject nesnesi oluşturur"""
        return GameObject("TestObject")
        
    def test_initialization(self, game_object):
        """Başlangıç değerlerini test eder"""
        assert game_object.name == "TestObject"
        assert isinstance(game_object.components, dict)
        assert len(game_object.components) == 0
        assert game_object.enabled is True
        
    def test_add_component(self, game_object):
        """Bileşen eklemeyi test eder"""
        class TestComponent:
            pass
            
        component = TestComponent()
        game_object.add_component("test", component)
        assert game_object.components["test"] == component
        
    def test_get_component(self, game_object):
        """Bileşen almayı test eder"""
        class TestComponent:
            pass
            
        component = TestComponent()
        game_object.add_component("test", component)
        
        # Var olan bileşen
        assert game_object.get_component("test") == component
        
        # Olmayan bileşen
        assert game_object.get_component("nonexistent") is None
        
    def test_update(self, game_object):
        """Güncelleme işlemini test eder"""
        class TestComponent:
            def __init__(self):
                self.updated = False
                
            def update(self, dt):
                self.updated = True
                
        component = TestComponent()
        game_object.add_component("test", component)
        
        # Normal güncelleme
        game_object.update(0.1)
        assert component.updated is True
        
        # Devre dışı nesne
        component.updated = False
        game_object.enabled = False
        game_object.update(0.1)
        assert component.updated is False
        
    def test_draw(self, game_object):
        """Çizim işlemini test eder"""
        class TestComponent:
            def __init__(self):
                self.drawn = False
                
            def draw(self, surface):
                self.drawn = True
                
        component = TestComponent()
        game_object.add_component("test", component)
        
        # Normal çizim
        surface = pygame.Surface((100, 100))
        game_object.draw(surface)
        assert component.drawn is True
        
        # Devre dışı nesne
        component.drawn = False
        game_object.enabled = False
        game_object.draw(surface)
        assert component.drawn is False
        
class TestGameSystem:
    """GameSystem sınıfı testleri"""
    
    @pytest.fixture
    def game_system(self):
        """Test için GameSystem nesnesi oluşturur"""
        return GameSystem("TestSystem")
        
    def test_initialization(self, game_system):
        """Başlangıç değerlerini test eder"""
        assert game_system.name == "TestSystem"
        assert game_system.enabled is True
        
    def test_lifecycle(self, game_system):
        """Yaşam döngüsü metodlarını test eder"""
        # initialize
        game_system.initialize()
        
        # update
        game_system.update(0.1)
        
        # update when disabled
        game_system.enabled = False
        game_system.update(0.1)
        
        # draw
        surface = pygame.Surface((100, 100))
        game_system.draw(surface)
        
        # cleanup
        game_system.cleanup() 