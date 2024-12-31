import pytest
import pygame
from engine.graphics.animation import Animation, AnimationManager

@pytest.fixture
def animation_frames():
    """Test için animasyon frame'leri oluşturur"""
    frames = []
    for i in range(3):
        surface = pygame.Surface((32, 32))
        surface.fill((i * 50, i * 50, i * 50))  # Farklı gri tonları
        frames.append(surface)
    return frames

def test_animation_initialization(animation_frames):
    """Animation başlatma testi"""
    animation = Animation(animation_frames, frame_duration=0.1, loop=True)
    assert len(animation.frames) == 3
    assert animation.frame_duration == 0.1
    assert animation.loop
    assert animation.current_frame == 0
    assert not animation.finished
    
def test_animation_update(animation_frames):
    """Animation güncelleme testi"""
    animation = Animation(animation_frames, frame_duration=0.1)
    
    # İlk frame
    assert animation.current_frame == 0
    
    # 0.05 saniye geçti (frame değişmemeli)
    animation.update(0.05)
    assert animation.current_frame == 0
    
    # 0.1 saniye daha geçti (sonraki frame'e geçmeli)
    animation.update(0.1)
    assert animation.current_frame == 1
    
def test_animation_looping(animation_frames):
    """Animation döngü testi"""
    animation = Animation(animation_frames, frame_duration=0.1, loop=True)
    
    # Tüm frame'leri geç
    for _ in range(len(animation_frames)):
        animation.update(0.1)
        
    # Döngü olduğu için başa dönmeli
    assert animation.current_frame == 0
    assert not animation.finished
    
def test_animation_no_loop(animation_frames):
    """Animation döngüsüz testi"""
    animation = Animation(animation_frames, frame_duration=0.1, loop=False)
    
    # Tüm frame'leri geç
    for _ in range(len(animation_frames) + 1):
        animation.update(0.1)
        
    # Son frame'de kalmalı ve bitmiş olmalı
    assert animation.current_frame == len(animation_frames) - 1
    assert animation.finished
    
class TestAnimationManager:
    """AnimationManager test sınıfı"""
    
    @pytest.fixture
    def animation_manager(self, animation_frames):
        """AnimationManager fixture'ı"""
        manager = AnimationManager()
        idle_anim = Animation(animation_frames, frame_duration=0.1)
        walk_anim = Animation(animation_frames, frame_duration=0.05)
        manager.add_animation("idle", idle_anim)
        manager.add_animation("walk", walk_anim)
        return manager
        
    def test_animation_switching(self, animation_manager):
        """Animasyon değiştirme testi"""
        # Başlangıçta idle animasyonu
        assert animation_manager.current_animation == "idle"
        
        # Walk animasyonuna geç
        animation_manager.play("walk")
        assert animation_manager.current_animation == "walk"
        assert animation_manager.is_playing("walk")
        
    def test_animation_update(self, animation_manager):
        """Animasyon güncelleme testi"""
        animation_manager.play("walk")
        
        # İlk frame
        frame1 = animation_manager.get_current_frame()
        
        # Güncelleme
        animation_manager.update(0.05)
        frame2 = animation_manager.get_current_frame()
        
        # Frame'ler farklı olmalı
        assert frame1 != frame2
        
    def test_animation_reset(self, animation_manager):
        """Animasyon sıfırlama testi"""
        animation_manager.play("walk")
        animation_manager.update(0.1)  # Bir frame ilerle
        
        # Sıfırla
        animation_manager.reset_current()
        assert animation_manager.animations["walk"].current_frame == 0 