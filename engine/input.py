import pygame
from typing import Dict, Set, Optional, Tuple, List
from enum import Enum, auto

class InputState(Enum):
    PRESSED = auto()
    HELD = auto()
    RELEASED = auto()

class InputSystem:
    def __init__(self):
        self._key_states: Dict[int, InputState] = {}
        self._mouse_states: Dict[int, InputState] = {}
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._mouse_motion: Tuple[int, int] = (0, 0)
        self._text_input: str = ""
        self._text_input_active: bool = False
        
    def update(self) -> None:
        """Her karede input durumlarını günceller"""
        # Tuş durumlarını güncelle
        keys = pygame.key.get_pressed()
        released_keys = set()
        
        for key, state in self._key_states.items():
            if state == InputState.PRESSED:
                self._key_states[key] = InputState.HELD
            elif state == InputState.RELEASED:
                released_keys.add(key)
                
        for key in released_keys:
            del self._key_states[key]
            
        # Fare durumlarını güncelle
        released_buttons = set()
        for button, state in self._mouse_states.items():
            if state == InputState.PRESSED:
                self._mouse_states[button] = InputState.HELD
            elif state == InputState.RELEASED:
                released_buttons.add(button)
                
        for button in released_buttons:
            del self._mouse_states[button]
            
        # Fare pozisyonunu güncelle
        self._mouse_position = pygame.mouse.get_pos()
        
        # Text input'u temizle
        self._text_input = ""
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Pygame olaylarını işler"""
        if event.type == pygame.KEYDOWN:
            self._key_states[event.key] = InputState.PRESSED
        elif event.type == pygame.KEYUP:
            self._key_states[event.key] = InputState.RELEASED
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_states[event.button] = InputState.PRESSED
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_states[event.button] = InputState.RELEASED
        elif event.type == pygame.MOUSEMOTION:
            self._mouse_motion = event.rel
        elif event.type == pygame.TEXTINPUT and self._text_input_active:
            self._text_input += event.text
            
    def is_key_pressed(self, key: int) -> bool:
        """Tuşa ilk kez basıldığını kontrol eder"""
        return self._key_states.get(key) == InputState.PRESSED
        
    def is_key_held(self, key: int) -> bool:
        """Tuşun basılı tutulduğunu kontrol eder"""
        return self._key_states.get(key) == InputState.HELD
        
    def is_key_released(self, key: int) -> bool:
        """Tuşun bırakıldığını kontrol eder"""
        return self._key_states.get(key) == InputState.RELEASED
        
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Fare düğmesine ilk kez basıldığını kontrol eder"""
        return self._mouse_states.get(button) == InputState.PRESSED
        
    def is_mouse_button_held(self, button: int) -> bool:
        """Fare düğmesinin basılı tutulduğunu kontrol eder"""
        return self._mouse_states.get(button) == InputState.HELD
        
    def is_mouse_button_released(self, button: int) -> bool:
        """Fare düğmesinin bırakıldığını kontrol eder"""
        return self._mouse_states.get(button) == InputState.RELEASED
        
    @property
    def mouse_position(self) -> Tuple[int, int]:
        """Fare pozisyonunu döndürür"""
        return self._mouse_position
        
    @property
    def mouse_motion(self) -> Tuple[int, int]:
        """Fare hareketini döndürür"""
        return self._mouse_motion
        
    @property
    def text_input(self) -> str:
        """Text input'u döndürür"""
        return self._text_input
        
    def start_text_input(self) -> None:
        """Text input modunu başlatır"""
        if not self._text_input_active:
            pygame.key.start_text_input()
            self._text_input_active = True
            
    def stop_text_input(self) -> None:
        """Text input modunu durdurur"""
        if self._text_input_active:
            pygame.key.stop_text_input()
            self._text_input_active = False 