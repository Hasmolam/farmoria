import pytest
import pygame
from engine.graphics.debug import DebugManager, DebugCategory, DebugLevel

@pytest.fixture
def debug_manager():
    pygame.init()
    manager = DebugManager()
    yield manager
    pygame.quit()

def test_initialization(debug_manager):
    """Test DebugManager initialization"""
    assert debug_manager.enabled == True
    assert len(debug_manager.messages) == len(DebugCategory)
    assert debug_manager.message_lifetime == 5.0
    assert debug_manager.max_messages == 10

def test_log_message(debug_manager):
    """Test logging messages"""
    message = "Test message"
    debug_manager.log(message)
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == 1
    assert debug_manager.messages[DebugCategory.GENERAL][0][0] == message

def test_log_with_category(debug_manager):
    """Test logging messages with specific category"""
    message = "Physics test"
    debug_manager.log(message, category=DebugCategory.PHYSICS)
    assert len(debug_manager.messages[DebugCategory.PHYSICS]) == 1
    assert debug_manager.messages[DebugCategory.PHYSICS][0][0] == message

def test_log_with_level(debug_manager):
    """Test logging messages with different levels"""
    message = "Warning test"
    debug_manager.log(message, level=DebugLevel.WARNING)
    assert debug_manager.messages[DebugCategory.GENERAL][0][1] == DebugLevel.WARNING

def test_max_messages(debug_manager):
    """Test maximum message limit"""
    for i in range(15):
        debug_manager.log(f"Message {i}")
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == debug_manager.max_messages

def test_update_lifetime(debug_manager):
    """Test message lifetime update"""
    debug_manager.log("Test message", lifetime=1.0)
    debug_manager.update(0.5)
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == 1
    debug_manager.update(0.6)
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == 0

def test_clear_messages(debug_manager):
    """Test clearing messages"""
    debug_manager.log("Test message 1")
    debug_manager.log("Test message 2", category=DebugCategory.PHYSICS)
    debug_manager.clear(DebugCategory.GENERAL)
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == 0
    assert len(debug_manager.messages[DebugCategory.PHYSICS]) == 1
    debug_manager.clear()
    assert all(len(messages) == 0 for messages in debug_manager.messages.values())

def test_enable_disable(debug_manager):
    """Test enabling/disabling debug system"""
    debug_manager.set_enabled(False)
    assert not debug_manager.is_enabled()
    debug_manager.log("Test message")
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == 0
    debug_manager.set_enabled(True)
    debug_manager.log("Test message")
    assert len(debug_manager.messages[DebugCategory.GENERAL]) == 1

def test_performance_metrics(debug_manager):
    """Test performance metrics"""
    debug_manager.start_performance_metric("test_metric")
    pygame.time.wait(100)  # Wait for 100ms
    duration = debug_manager.end_performance_metric("test_metric")
    assert duration is not None
    assert duration >= 0.1  # Should be at least 100ms

def test_get_performance_stats(debug_manager):
    """Test getting performance statistics"""
    debug_manager.start_performance_metric("test_metric")
    stats = debug_manager.get_performance_stats()
    assert "test_metric" in stats
    assert stats["test_metric"] >= 0

def test_draw(debug_manager):
    """Test drawing debug messages"""
    surface = pygame.Surface((800, 600))
    debug_manager.log("Test message")
    debug_manager.draw(surface)
    # Drawing test is minimal since we can't easily verify the visual output
    # But we can verify it doesn't raise any exceptions 