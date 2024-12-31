import pytest
from engine.core.scene import Scene, SceneManager
from engine.core.base import GameObject, GameSystem

def test_scene_initialization():
    """Scene başlatma testi"""
    scene = Scene("test_scene")
    assert scene.name == "test_scene"
    assert len(scene.objects) == 0
    assert len(scene.systems) == 0
    assert not scene.active
    
def test_scene_object_management():
    """Scene nesne yönetimi testi"""
    scene = Scene("test_scene")
    obj = GameObject()
    
    # Nesne ekleme
    scene.add_object(obj)
    assert len(scene.objects) == 1
    assert obj in scene.objects
    
    # Nesne kaldırma
    scene.remove_object(obj)
    assert len(scene.objects) == 0
    assert obj not in scene.objects
    
def test_scene_system_management():
    """Scene sistem yönetimi testi"""
    scene = Scene("test_scene")
    system = GameSystem("test_system")
    
    # Sistem ekleme
    scene.add_system(system)
    assert len(scene.systems) == 1
    assert system in scene.systems
    
    # Sistem kaldırma
    scene.remove_system(system)
    assert len(scene.systems) == 0
    assert system not in scene.systems
    
def test_scene_activation():
    """Scene aktivasyon testi"""
    scene = Scene("test_scene")
    
    # Başlangıçta pasif
    assert not scene.active
    
    # Aktifleştirme
    scene.on_enter()
    assert scene.active
    
    # Pasifleştirme
    scene.on_exit()
    assert not scene.active
    
class TestSceneManager:
    """SceneManager test sınıfı"""
    
    @pytest.fixture
    def scene_manager(self):
        """SceneManager fixture'ı"""
        return SceneManager(None)
        
    def test_scene_management(self, scene_manager):
        """Scene yönetimi testi"""
        scene = Scene("test_scene")
        
        # Scene ekleme
        scene_manager.add_scene(scene)
        assert "test_scene" in scene_manager.scenes
        assert scene_manager.get_scene("test_scene") == scene
        
        # Scene aktifleştirme
        scene_manager.set_scene("test_scene")
        assert scene_manager.active_scene == scene
        
        # Scene kaldırma
        scene_manager.remove_scene("test_scene")
        assert "test_scene" not in scene_manager.scenes
        assert scene_manager.active_scene is None 