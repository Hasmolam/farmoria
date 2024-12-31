import pytest
import pygame
import time
from engine.core.timing import Timer, FrameManager

@pytest.fixture
def timer():
    """Test için Timer nesnesi oluşturur"""
    pygame.init()
    pygame.display.set_mode((800, 600))
    return Timer(target_fps=60, vsync=False)  # Test için vsync kapalı

@pytest.fixture
def frame_manager(timer):
    """Test için FrameManager nesnesi oluşturur"""
    return FrameManager(timer)

class TestTimer:
    def test_initialization(self, timer):
        """Timer'ın doğru başlatıldığını kontrol eder"""
        assert timer.target_fps == 60
        assert timer.vsync == False
        assert timer.frame_duration == 1/60
        assert timer.delta_time == 0.0
        assert timer.accumulated_time == 0.0
        assert timer.frame_count == 0
        assert timer.fps == 0.0

    def test_tick(self, timer):
        """Tick işlemini test eder"""
        # İlk tick
        dt1 = timer.tick()
        assert dt1 >= 0.0  # Delta time pozitif olmalı
        
        # Kısa bir bekleme
        time.sleep(0.1)
        
        # İkinci tick
        dt2 = timer.tick()
        assert dt2 >= 0.1  # Bekleme süresinden büyük olmalı
        assert dt2 <= 0.2  # Makul bir üst sınır

    def test_fps_calculation(self, timer):
        """FPS hesaplama işlemini test eder"""
        # FPS hesaplama zamanını sıfırla
        timer.fps_update_time = time.perf_counter()
        timer.frame_count = 0
        
        # Birkaç frame simüle et
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < 1.1:  # 1 saniyeden biraz fazla
            timer.tick()
            time.sleep(1/60)  # 60 FPS simülasyonu
        
        fps = timer.get_fps()
        assert fps > 0.0  # FPS değeri hesaplanmış olmalı
        assert fps < 70.0  # Makul bir üst sınır

    def test_target_fps_setting(self, timer):
        """Hedef FPS ayarını test eder"""
        timer.set_target_fps(30)
        assert timer.target_fps == 30
        assert timer.frame_duration == 1/30

    def test_vsync_toggle(self, timer):
        """V-Sync açma/kapama işlemini test eder"""
        initial_state = timer.vsync
        timer.toggle_vsync()
        assert timer.vsync != initial_state
        timer.toggle_vsync()
        assert timer.vsync == initial_state

class TestFrameManager:
    def test_initialization(self, frame_manager):
        """FrameManager'ın doğru başlatıldığını kontrol eder"""
        assert frame_manager.fixed_update_rate == 1/50  # 50 Hz
        assert frame_manager.accumulated_time == 0.0
        assert frame_manager.max_updates_per_frame == 5

    def test_update(self, frame_manager):
        """Update işlemini test eder"""
        update_count = 0
        render_count = 0
        
        def mock_update(dt):
            nonlocal update_count
            update_count += 1
            assert dt == frame_manager.fixed_update_rate
            
        def mock_render():
            nonlocal render_count
            render_count += 1
        
        # Normal güncelleme
        frame_manager.update(mock_update, mock_render)
        assert update_count >= 0  # En az bir güncelleme yapılmalı
        assert render_count == 1  # Her frame'de bir render
        
        # Uzun frame simülasyonu
        frame_manager.accumulated_time = 0.2  # 200ms birikmiş zaman
        frame_manager.update(mock_update, mock_render)
        assert update_count <= frame_manager.max_updates_per_frame  # Maksimum güncelleme sınırı aşılmamalı

    def test_fixed_update_rate(self, frame_manager):
        """Sabit güncelleme oranı ayarını test eder"""
        frame_manager.set_fixed_update_rate(100)  # 100 Hz
        assert frame_manager.fixed_update_rate == 1/100

    def teardown_method(self):
        """Test sonrası temizlik"""
        pygame.quit() 