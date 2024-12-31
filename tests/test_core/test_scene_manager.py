import pytest
from engine.core.scene import Scene, SceneManager
from engine.core.base import GameObject, GameSystem

class TestScene:
    """Scene test sınıfı"""
    
    @pytest.fixture
    def empty_scene(self):
        """Boş sahne fixture'ı"""
        return Scene("test_scene")
        
    @pytest.fixture
    def game_object(self):
        """Test için GameObject fixture'ı"""
        return GameObject("test_object")
        
    @pytest.fixture
    def game_system(self):
        """Test için GameSystem fixture'ı"""
        return GameSystem()
        
    def test_scene_initialization(self, empty_scene):
        """Sahne başlatma testi"""
        assert empty_scene.name == "test_scene"
        assert len(empty_scene.objects) == 0
        assert len(empty_scene.systems) == 0
        assert not empty_scene.active
        
    def test_add_game_object(self, empty_scene, game_object):
        """GameObject ekleme testi"""
        empty_scene.add_object(game_object)
        assert len(empty_scene.objects) == 1
        assert game_object in empty_scene.objects
        
    def test_remove_game_object(self, empty_scene, game_object):
        """GameObject silme testi"""
        empty_scene.add_object(game_object)
        empty_scene.remove_object(game_object)
        assert len(empty_scene.objects) == 0
        assert game_object not in empty_scene.objects
        
    def test_add_system(self, empty_scene, game_system):
        """GameSystem ekleme testi"""
        empty_scene.add_system(game_system)
        assert len(empty_scene.systems) == 1
        assert game_system in empty_scene.systems
        
    def test_remove_system(self, empty_scene, game_system):
        """GameSystem silme testi"""
        empty_scene.add_system(game_system)
        empty_scene.remove_system(game_system)
        assert len(empty_scene.systems) == 0
        assert game_system not in empty_scene.systems
        
    def test_scene_activation(self, empty_scene):
        """Sahne aktivasyon testi"""
        empty_scene.activate()
        assert empty_scene.active
        empty_scene.deactivate()
        assert not empty_scene.active
        
class TestSceneManager:
    """SceneManager test sınıfı"""
    
    @pytest.fixture
    def scene_manager(self):
        """SceneManager fixture'ı"""
        class MockEngine:
            pass
        engine = MockEngine()
        return SceneManager(engine)
        
    @pytest.fixture
    def test_scene(self):
        """Test için Scene fixture'ı"""
        return Scene("test_scene")
        
    def test_add_scene(self, scene_manager, test_scene):
        """Sahne ekleme testi"""
        scene_manager.add_scene(test_scene)
        assert len(scene_manager.scenes) == 1
        assert test_scene in scene_manager.scenes.values()
        
    def test_get_scene(self, scene_manager, test_scene):
        """Sahne alma testi"""
        scene_manager.add_scene(test_scene)
        retrieved_scene = scene_manager.get_scene("test_scene")
        assert retrieved_scene == test_scene
        
    def test_remove_scene(self, scene_manager, test_scene):
        """Sahne silme testi"""
        scene_manager.add_scene(test_scene)
        scene_manager.remove_scene("test_scene")
        assert len(scene_manager.scenes) == 0
        assert "test_scene" not in scene_manager.scenes
        
    def test_activate_scene(self, scene_manager, test_scene):
        """Sahne aktivasyon testi"""
        scene_manager.add_scene(test_scene)
        scene_manager.activate_scene("test_scene")
        assert test_scene.active
        assert scene_manager.active_scene == test_scene
        
    def test_deactivate_scene(self, scene_manager, test_scene):
        """Sahne deaktivasyon testi"""
        scene_manager.add_scene(test_scene)
        scene_manager.activate_scene("test_scene")
        scene_manager.deactivate_scene("test_scene")
        assert not test_scene.active
        assert scene_manager.active_scene is None 