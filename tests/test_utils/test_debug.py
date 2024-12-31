import pytest
import pygame
import time
from engine.utils.debug import DebugSystem, DebugLevel

@pytest.fixture
def debug_system():
    pygame.init()
    system = DebugSystem()
    system.initialize()
    yield system
    pygame.quit()

def test_initialization(debug_system):
    """Test DebugSystem initialization"""
    assert debug_system.enabled == True
    assert debug_system.show_fps == True
    assert debug_system.show_memory == True
    assert debug_system.show_physics == True
    assert debug_system.fps_font is not None
    assert len(debug_system.frame_times) == 0
    assert len(debug_system.messages) == 0

def test_logging(debug_system):
    """Test logging messages"""
    debug_system.log("Test message", DebugLevel.INFO)
    assert len(debug_system.messages) == 1
    assert debug_system.messages[0][0] == "Test message"
    assert debug_system.messages[0][1] == DebugLevel.INFO

def test_message_lifetime(debug_system):
    """Test message lifetime"""
    debug_system.message_lifetime = 0.1  # Set short lifetime for testing
    debug_system.log("Test message")
    assert len(debug_system.messages) == 1
    time.sleep(0.2)  # Wait for message to expire
    debug_system.log("New message")  # This will trigger cleanup
    assert len(debug_system.messages) == 1
    assert debug_system.messages[0][0] == "New message"

def test_fps_calculation(debug_system):
    """Test FPS calculation"""
    # Simulate frame times
    debug_system.frame_times = [0.016667] * 10  # 60 FPS
    assert abs(debug_system.get_fps() - 60.0) < 1.0

def test_performance_profiling(debug_system):
    """Test performance profiling"""
    debug_system.start_profile("test")
    time.sleep(0.1)
    debug_system.end_profile("test")
    assert "test" in debug_system.performance_metrics
    assert debug_system.performance_metrics["test"] >= 0.1

def test_disabled_system(debug_system):
    """Test disabled debug system"""
    debug_system.enabled = False
    debug_system.log("Test message")
    assert len(debug_system.messages) == 0
    
    debug_system.start_profile("test")
    debug_system.end_profile("test")
    assert debug_system.performance_metrics.get("test") is None

def test_max_frame_samples(debug_system):
    """Test maximum frame samples"""
    for _ in range(40):  # More than max_frame_samples
        debug_system.update_fps()
    assert len(debug_system.frame_times) == debug_system.max_frame_samples

def test_clear(debug_system):
    """Test clearing debug data"""
    debug_system.log("Test message")
    debug_system.frame_times.append(0.016667)
    debug_system.performance_metrics["test"] = 0.1
    
    debug_system.clear()
    assert len(debug_system.messages) == 0
    assert len(debug_system.frame_times) == 0
    assert "test" not in debug_system.performance_metrics
    assert debug_system.performance_metrics["update_time"] == 0.0

def test_draw(debug_system):
    """Test drawing debug information"""
    surface = pygame.Surface((800, 600))
    debug_system.log("Test message", DebugLevel.WARNING)
    debug_system.performance_metrics["test"] = 0.1
    debug_system.draw(surface)
    # Visual test would require pixel color checking 