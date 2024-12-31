import pytest
import pygame
from engine.ui.manager import UIManager
from engine.ui.base import UIElement, Button

@pytest.fixture
def ui_manager():
    pygame.init()
    manager = UIManager()
    manager.initialize(800, 600)
    yield manager
    pygame.quit()

def test_initialization(ui_manager):
    """Test UIManager initialization"""
    assert ui_manager.root.rect.width == 800
    assert ui_manager.root.rect.height == 600
    assert ui_manager.focused_element is None
    assert ui_manager.default_font is not None

def test_add_remove_element(ui_manager):
    """Test adding and removing UI elements"""
    element = UIElement(10, 20, 100, 50)
    ui_manager.add_element(element)
    assert element in ui_manager.root.children
    
    ui_manager.remove_element(element)
    assert element not in ui_manager.root.children

def test_handle_mouse_event(ui_manager):
    """Test mouse event handling"""
    button = Button(10, 20, 100, 50, "Test Button")
    ui_manager.add_element(button)
    
    # Test mouse motion
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (15, 25)})
    assert ui_manager.handle_event(motion_event)
    assert button.is_hovered
    
    # Test mouse click
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (15, 25)})
    assert ui_manager.handle_event(click_event)
    assert button.is_pressed

def test_get_element_at(ui_manager):
    """Test getting element at position"""
    button1 = Button(10, 20, 100, 50, "Button 1")
    button2 = Button(120, 20, 100, 50, "Button 2")
    ui_manager.add_element(button1)
    ui_manager.add_element(button2)
    
    # Test finding elements
    element = ui_manager.get_element_at((15, 25))
    assert element == button1
    
    element = ui_manager.get_element_at((125, 25))
    assert element == button2
    
    element = ui_manager.get_element_at((0, 0))
    assert element is None

def test_focus_handling(ui_manager):
    """Test focus handling"""
    button = Button(10, 20, 100, 50, "Test Button")
    ui_manager.add_element(button)
    
    # Set focus
    ui_manager.set_focus(button)
    assert ui_manager.focused_element == button
    
    # Clear focus
    ui_manager.set_focus(None)
    assert ui_manager.focused_element is None
    
    # Remove focused element
    ui_manager.set_focus(button)
    ui_manager.remove_element(button)
    assert ui_manager.focused_element is None

def test_update_and_draw(ui_manager):
    """Test update and draw methods"""
    surface = pygame.Surface((800, 600))
    button = Button(10, 20, 100, 50, "Test Button")
    ui_manager.add_element(button)
    
    # Test that update and draw don't raise exceptions
    ui_manager.update(0.1)
    ui_manager.draw(surface)

def test_disabled_manager(ui_manager):
    """Test disabled UI manager"""
    button = Button(10, 20, 100, 50, "Test Button")
    ui_manager.add_element(button)
    
    ui_manager.enabled = False
    event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (15, 25)})
    assert not ui_manager.handle_event(event)
    assert not button.is_hovered 