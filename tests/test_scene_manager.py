import pytest
import pygame
import asyncio
from engine.scene import Scene, SceneManager, SceneState, SceneError

# Test için özel Scene sınıfı
class TestScene(Scene):
    def __init__(self):
        super().__init__()
        self.enter_called = False
        self.exit_called = False
        self.update_called = False
        self.draw_called = False
        self.preload_called = False
        
    def on_enter(self, data=None):
        super().on_enter(data)
        self.enter_called = True
        
    def on_exit(self):
        super().on_exit()
        self.exit_called = True
        
    def _update_scene(self, dt):
        self.update_called = True
        
    def _draw_scene(self, screen):
        self.draw_called = True
        
    async def preload(self):
        await super().preload()
        self.preload_called = True
        self.loading_progress = 1.0

class MockEngine:
    pass

@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def screen():
    return pygame.Surface((800, 600))

@pytest.fixture
def engine():
    return MockEngine()

@pytest.fixture
def scene_manager(engine):
    return SceneManager(engine)

@pytest.fixture
def test_scene():
    return TestScene()

# Temel işlevsellik testleri
def test_scene_initialization(test_scene):
    assert test_scene.state == SceneState.LOADING
    assert test_scene.transition_alpha == 255
    assert not test_scene.is_paused

def test_add_scene(scene_manager, test_scene):
    scene_manager.add_scene("test", test_scene)
    assert "test" in scene_manager.scenes
    assert scene_manager.scenes["test"] == test_scene

def test_set_scene(scene_manager, test_scene):
    scene_manager.add_scene("test", test_scene)
    scene_manager.set_scene("test", {"test_data": 123})
    assert scene_manager.current_scene == test_scene
    assert test_scene.data == {"test_data": 123}
    assert test_scene.enter_called

def test_scene_transition(scene_manager, test_scene, screen):
    scene_manager.add_scene("test", test_scene)
    scene_manager.set_scene("test")
    
    # Scene'i çıkışa zorla
    test_scene.on_exit()
    assert test_scene.is_transitioning
    
    # Geçiş animasyonunu test et
    scene_manager.update(0.1)  # dt = 0.1 saniye
    assert test_scene.transition_alpha < 255  # Şimdi bu çalışmalı

# Scene Stack testleri
def test_scene_stack(scene_manager):
    scene1 = TestScene()
    scene2 = TestScene()
    
    scene_manager.add_scene("scene1", scene1)
    scene_manager.add_scene("scene2", scene2)
    
    scene_manager.set_scene("scene1")
    scene_manager.set_scene("scene2")
    
    assert scene_manager.current_scene == scene2
    assert "scene1" in scene_manager.scene_stack
    
    scene_manager.pop_scene()
    assert scene_manager.current_scene == scene1

# Hata yönetimi testleri
def test_invalid_scene(scene_manager):
    with pytest.raises(SceneError):
        scene_manager.set_scene("nonexistent")

def test_scene_error_handling(scene_manager):
    class ErrorScene(Scene):
        def on_enter(self, data=None):
            raise Exception("Test error")
    
    error_scene = ErrorScene()
    scene_manager.add_scene("error", error_scene)
    
    with pytest.raises(SceneError):
        scene_manager.set_scene("error")

# Durum yönetimi testleri
def test_scene_pause_resume(scene_manager, test_scene):
    scene_manager.add_scene("test", test_scene)
    scene_manager.set_scene("test")
    
    scene_manager.pause_current_scene()
    assert test_scene.is_paused
    assert test_scene.state == SceneState.PAUSED
    
    scene_manager.resume_current_scene()
    assert not test_scene.is_paused
    assert test_scene.state == SceneState.READY

# Önbellek testleri
@pytest.mark.asyncio
async def test_scene_preload(scene_manager, test_scene):
    scene_manager.add_scene("test", test_scene)
    await scene_manager.preload_scene("test")
    
    assert test_scene.preload_called
    assert "test" in scene_manager.cached_scenes
    assert test_scene.loading_progress == 1.0

def test_cache_clear(scene_manager, test_scene):
    scene_manager.add_scene("test", test_scene)
    scene_manager.cached_scenes.add("test")
    
    scene_manager.clear_cache()
    assert "test" not in scene_manager.cached_scenes

# Çizim ve güncelleme testleri
def test_scene_update_draw(scene_manager, test_scene, screen):
    scene_manager.add_scene("test", test_scene)
    scene_manager.set_scene("test")
    
    scene_manager.update(0.1)
    assert test_scene.update_called
    
    scene_manager.draw(screen)
    assert test_scene.draw_called

# Yükleme ekranı testi
def test_loading_screen(test_scene, screen):
    test_scene.state = SceneState.LOADING
    test_scene.loading_progress = 0.5
    test_scene.draw(screen)
    # Yükleme ekranının çizildiğini kontrol et
    # (Piksel kontrolü yapılabilir, ama bu basit test için gerek yok)

if __name__ == "__main__":
    pytest.main([__file__]) 