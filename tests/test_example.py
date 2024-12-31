import pytest
from engine.core.core import FarmoriaEngine
import pygame

def test_engine_initialization():
    """Test engine başlatma işlemini kontrol eder."""
    engine = FarmoriaEngine(800, 600, "Test Game")
    assert engine is not None
    assert engine.screen is not None
    assert engine.running == True
    
def test_engine_window_size():
    """Test pencere boyutlarını kontrol eder."""
    width, height = 800, 600
    engine = FarmoriaEngine(width, height, "Test Game")
    screen_width = engine.screen.get_width()
    screen_height = engine.screen.get_height()
    assert screen_width == width
    assert screen_height == height

@pytest.mark.parametrize("title", ["Test Game", "My Game", "Awesome Game"])
def test_engine_title(title):
    """Test oyun başlığını kontrol eder."""
    engine = FarmoriaEngine(800, 600, title)
    assert pygame.display.get_caption()[0] == title 