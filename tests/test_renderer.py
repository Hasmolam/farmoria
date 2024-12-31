import pytest
import pygame
from engine.renderer import Renderer, RenderObject, RenderLayer

@pytest.fixture
def renderer():
    pygame.init()
    return Renderer()

@pytest.fixture
def test_surface():
    return pygame.Surface((100, 100))

@pytest.fixture
def target_surface():
    return pygame.Surface((800, 600))

def test_renderer_initialization(renderer):
    """Renderer'ın doğru şekilde başlatıldığını kontrol et"""
    assert renderer.layers == {}
    assert renderer.camera_pos == [0, 0]
    assert renderer.camera_zoom == 1.0
    assert renderer.post_processing_effects == []

def test_create_layer(renderer):
    """Katman oluşturma işlevini test et"""
    layer = renderer.create_layer(1)
    assert isinstance(layer, RenderLayer)
    assert layer.layer_id == 1
    assert 1 in renderer.layers

def test_add_remove_object(renderer, test_surface):
    """Nesne ekleme ve çıkarma işlevlerini test et"""
    obj = RenderObject(
        surface=test_surface,
        position=(100, 100)
    )
    
    # Nesne ekleme testi
    renderer.add_object(obj)
    assert obj in renderer.layers[0].objects
    
    # Nesne çıkarma testi
    renderer.remove_object(obj)
    assert obj not in renderer.layers[0].objects

def test_camera_operations(renderer):
    """Kamera işlevlerini test et"""
    # Kamera pozisyonu ayarlama
    renderer.set_camera(100, 200)
    assert renderer.camera_pos == [100, 200]
    
    # Kamera hareketi
    renderer.move_camera(50, -30)
    assert renderer.camera_pos == [150, 170]
    
    # Zoom kontrolü
    renderer.set_zoom(2.0)
    assert renderer.camera_zoom == 2.0
    
    # Minimum zoom sınırı
    renderer.set_zoom(0.05)
    assert renderer.camera_zoom == 0.1
    
    # Maksimum zoom sınırı
    renderer.set_zoom(11.0)
    assert renderer.camera_zoom == 10.0

def test_world_to_screen_conversion(renderer):
    """Dünya koordinatlarından ekran koordinatlarına dönüşümü test et"""
    renderer.set_camera(100, 100)
    renderer.set_zoom(2.0)
    
    screen_x, screen_y = renderer.world_to_screen(200, 200)
    assert screen_x == 200  # (200 - 100) * 2
    assert screen_y == 200  # (200 - 100) * 2

def test_render_object_properties(renderer, test_surface, target_surface):
    """RenderObject özelliklerinin doğru çalıştığını test et"""
    obj = RenderObject(
        surface=test_surface,
        position=(100, 100),
        layer=1,
        alpha=128,
        scale=(2.0, 2.0),
        rotation=45
    )
    
    renderer.add_object(obj)
    
    # Görünürlük kontrolü
    obj.visible = False
    renderer.render(target_surface)
    
    # Alpha değeri kontrolü
    obj.visible = True
    obj.alpha = 128
    renderer.render(target_surface)
    
    # Ölçekleme kontrolü
    obj.scale = (2.0, 2.0)
    renderer.render(target_surface)
    
    # Rotasyon kontrolü
    obj.rotation = 45
    renderer.render(target_surface)

def test_layer_sorting(renderer, test_surface):
    """Katmanların doğru sıralandığını test et"""
    obj1 = RenderObject(surface=test_surface, position=(0, 0), layer=2)
    obj2 = RenderObject(surface=test_surface, position=(0, 0), layer=1)
    obj3 = RenderObject(surface=test_surface, position=(0, 0), layer=3)
    
    renderer.add_object(obj1)
    renderer.add_object(obj2)
    renderer.add_object(obj3)
    
    sorted_layers = sorted(renderer.layers.items(), key=lambda x: x[0])
    assert [layer_id for layer_id, _ in sorted_layers] == [1, 2, 3]

def test_layer_visibility(renderer, test_surface, target_surface):
    """Katman görünürlüğünün kontrolünü test et"""
    obj = RenderObject(surface=test_surface, position=(0, 0), layer=1)
    renderer.add_object(obj)
    
    # Katmanı görünmez yap
    renderer.layers[1].visible = False
    renderer.render(target_surface)
    
    # Katmanı görünür yap
    renderer.layers[1].visible = True
    renderer.render(target_surface) 