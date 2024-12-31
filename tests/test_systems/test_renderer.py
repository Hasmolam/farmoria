import pytest
import pygame
from engine.systems.renderer import Renderer, RenderObject, RenderLayer

@pytest.fixture
def renderer():
    """Renderer fixture'ı"""
    screen = pygame.Surface((800, 600))
    return Renderer(screen)

@pytest.fixture
def render_object():
    """RenderObject fixture'ı"""
    surface = pygame.Surface((32, 32))
    surface.fill((255, 0, 0))  # Kırmızı kare
    return RenderObject(surface, x=100, y=100, layer=RenderLayer.MIDDLE)

class TestRenderer:
    """Renderer test sınıfı"""
    
    def test_renderer_initialization(self, renderer):
        """Renderer başlatma testi"""
        assert isinstance(renderer.screen, pygame.Surface)
        assert len(renderer.layers) == len(RenderLayer)
        
    def test_add_object(self, renderer, render_object):
        """Nesne ekleme testi"""
        renderer.add_object(render_object)
        assert render_object in renderer.layers[RenderLayer.MIDDLE]
        
    def test_remove_object(self, renderer, render_object):
        """Nesne silme testi"""
        renderer.add_object(render_object)
        renderer.remove_object(render_object)
        assert render_object not in renderer.layers[RenderLayer.MIDDLE]
        
    def test_clear_layer(self, renderer, render_object):
        """Katman temizleme testi"""
        renderer.add_object(render_object)
        renderer.clear_layer(RenderLayer.MIDDLE)
        assert len(renderer.layers[RenderLayer.MIDDLE]) == 0
        
    def test_clear_all(self, renderer, render_object):
        """Tüm katmanları temizleme testi"""
        renderer.add_object(render_object)
        renderer.clear_all()
        for layer in renderer.layers.values():
            assert len(layer) == 0
            
class TestRenderObject:
    """RenderObject test sınıfı"""
    
    def test_object_initialization(self, render_object):
        """RenderObject başlatma testi"""
        assert render_object.x == 100
        assert render_object.y == 100
        assert render_object.layer == RenderLayer.MIDDLE
        assert isinstance(render_object.surface, pygame.Surface)
        
    def test_object_position(self, render_object):
        """Pozisyon ayarlama testi"""
        render_object.x = 200
        render_object.y = 300
        assert render_object.x == 200
        assert render_object.y == 300
        
    def test_object_layer(self, render_object):
        """Katman ayarlama testi"""
        render_object.layer = RenderLayer.TOP
        assert render_object.layer == RenderLayer.TOP
        
    def test_object_visibility(self, render_object):
        """Görünürlük ayarlama testi"""
        assert render_object.visible
        render_object.visible = False
        assert not render_object.visible 