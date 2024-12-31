"""
UI base modülü testleri.
"""

import pytest
import pygame
from engine.ui.base import UIElement, Button, Panel

@pytest.fixture
def ui_element():
    """Test için UI elemanı oluşturur"""
    return UIElement(10, 20, 100, 50)

@pytest.fixture
def button():
    """Test için buton oluşturur"""
    return Button(10, 20, 100, 50, "Test Button")

@pytest.fixture
def panel():
    """Test için panel oluşturur"""
    return Panel(10, 20, 200, 300)

def test_ui_element_initialization(ui_element):
    """UI elemanı başlatma testi"""
    assert ui_element.rect.x == 10
    assert ui_element.rect.y == 20
    assert ui_element.rect.width == 100
    assert ui_element.rect.height == 50
    assert ui_element.parent is None
    assert len(ui_element.children) == 0
    assert ui_element.visible is True
    assert ui_element.enabled is True

def test_add_child(ui_element):
    """Alt eleman ekleme testi"""
    child = UIElement(0, 0, 50, 30)
    ui_element.add_child(child)
    assert child in ui_element.children
    assert child.parent == ui_element
    assert len(ui_element.children) == 1

def test_remove_child(ui_element):
    """Alt eleman kaldırma testi"""
    child = UIElement(0, 0, 50, 30)
    ui_element.add_child(child)
    ui_element.remove_child(child)
    assert child not in ui_element.children
    assert child.parent is None
    assert len(ui_element.children) == 0

def test_get_absolute_position(ui_element):
    """Mutlak pozisyon hesaplama testi"""
    parent = UIElement(5, 10, 200, 150)
    parent.add_child(ui_element)
    abs_x, abs_y = ui_element.get_absolute_position()
    assert abs_x == 15  # 5 + 10
    assert abs_y == 30  # 10 + 20

def test_contains_point(ui_element):
    """Nokta içerme testi"""
    assert ui_element.contains_point((15, 25)) is True
    assert ui_element.contains_point((5, 15)) is False
    assert ui_element.contains_point((150, 100)) is False

def test_button_initialization(button):
    """Buton başlatma testi"""
    assert button.text == "Test Button"
    assert button.text_color == (0, 0, 0)
    assert button.is_hovered is False
    assert button.is_pressed is False
    assert button.on_click is None

def test_button_click_event(button):
    """Buton tıklama olayı testi"""
    clicked = False
    def on_click():
        nonlocal clicked
        clicked = True
    
    button.on_click = on_click
    
    # Mouse down event
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (15, 25)})
    assert button.handle_event(event) is True
    assert button.is_pressed is True
    
    # Mouse up event
    event = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (15, 25)})
    assert button.handle_event(event) is True
    assert button.is_pressed is False
    assert clicked is True

def test_panel_initialization(panel):
    """Panel başlatma testi"""
    assert panel.rect.x == 10
    assert panel.rect.y == 20
    assert panel.rect.width == 200
    assert panel.rect.height == 300
    assert panel.padding == 0

def test_panel_auto_layout(panel):
    """Panel otomatik düzenleme testi"""
    button1 = Button(0, 0, 100, 30, "Button 1")
    button2 = Button(0, 0, 100, 30, "Button 2")
    panel.add_child(button1)
    panel.add_child(button2)
    
    panel.set_padding(10)
    panel.auto_layout(spacing=5)
    
    assert button1.rect.x == 10  # padding
    assert button1.rect.y == 10  # padding
    assert button1.rect.width == 180  # panel width - 2 * padding
    
    assert button2.rect.x == 10  # padding
    assert button2.rect.y == 45  # padding + button1 height + spacing
    assert button2.rect.width == 180  # panel width - 2 * padding 