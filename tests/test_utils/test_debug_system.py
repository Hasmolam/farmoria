import pytest
import pygame
import time
from engine.utils.debug import DebugSystem, DebugLevel

@pytest.fixture
def debug_system():
    """Test için debug sistemi oluşturur"""
    system = DebugSystem()
    system.initialize()
    return system

class TestDebugSystem:
    def test_initialization(self, debug_system):
        """Debug sisteminin doğru başlatıldığını kontrol eder"""
        assert debug_system.enabled == True
        assert debug_system.show_fps == True
        assert debug_system.show_memory == True
        assert debug_system.show_physics == True
        assert len(debug_system.frame_times) == 0
        assert len(debug_system.messages) == 0
        assert debug_system.message_lifetime == 5.0
        assert "update_time" in debug_system.performance_metrics
        assert "render_time" in debug_system.performance_metrics
        assert "physics_time" in debug_system.performance_metrics

    def test_logging(self, debug_system):
        """Debug mesajı ekleme işlemini test eder"""
        # Normal mesaj
        debug_system.log("Test message")
        assert len(debug_system.messages) == 1
        msg, level, _ = debug_system.messages[0]
        assert msg == "Test message"
        assert level == DebugLevel.INFO

        # Farklı seviyede mesaj
        debug_system.log("Warning message", DebugLevel.WARNING)
        assert len(debug_system.messages) == 2
        msg, level, _ = debug_system.messages[1]
        assert msg == "Warning message"
        assert level == DebugLevel.WARNING

        # Sistem kapalıyken mesaj
        debug_system.enabled = False
        debug_system.log("Disabled message")
        assert len(debug_system.messages) == 2  # Yeni mesaj eklenmemeli

    def test_message_lifetime(self, debug_system):
        """Mesaj ömrü kontrolünü test eder"""
        debug_system.message_lifetime = 0.1  # Test için kısa ömür
        
        # Mesaj ekle
        debug_system.log("Test message")
        assert len(debug_system.messages) == 1
        
        # Biraz bekle
        time.sleep(0.2)
        
        # Yeni mesaj ekleyerek eski mesajların temizlenmesini tetikle
        debug_system.log("New message")
        assert len(debug_system.messages) == 1  # Eski mesaj silinmiş olmalı
        assert debug_system.messages[0][0] == "New message"

    def test_fps_calculation(self, debug_system):
        """FPS hesaplama işlemini test eder"""
        # Sabit frame süresi simüle et
        frame_time = 1/60  # 60 FPS
        for _ in range(10):
            debug_system.frame_times.append(frame_time)
        
        fps = debug_system.get_fps()
        assert abs(fps - 60.0) < 0.1  # Küçük bir hata payı ile kontrol et

    def test_performance_profiling(self, debug_system):
        """Performans profilleme işlemini test eder"""
        # Profilleme başlat
        debug_system.start_profile("test_operation")
        time.sleep(0.1)  # İşlem simülasyonu
        debug_system.end_profile("test_operation")
        
        # Sonuçları kontrol et
        assert "test_operation" in debug_system.performance_metrics
        assert debug_system.performance_metrics["test_operation"] >= 0.1

        # Sistem kapalıyken profilleme
        debug_system.enabled = False
        debug_system.start_profile("disabled_test")
        debug_system.end_profile("disabled_test")
        assert "disabled_test" not in debug_system.performance_metrics

    def test_clear(self, debug_system):
        """Temizleme işlemini test eder"""
        # Veri ekle
        debug_system.log("Test message")
        debug_system.frame_times.append(1/60)
        debug_system.performance_metrics["test"] = 0.1
        
        # Temizle
        debug_system.clear()
        
        # Kontrol et
        assert len(debug_system.messages) == 0
        assert len(debug_system.frame_times) == 0
        assert debug_system.performance_metrics == {
            "update_time": 0.0,
            "render_time": 0.0,
            "physics_time": 0.0
        }

    @pytest.mark.skip(reason="pygame.font.Font kullanımı nedeniyle atlanıyor")
    def test_drawing(self, debug_system):
        """Çizim işlemini test eder"""
        surface = pygame.Surface((800, 600))
        
        # Test verisi ekle
        debug_system.log("Test message")
        debug_system.frame_times.append(1/60)
        debug_system.performance_metrics["test"] = 0.1
        
        # Çiz
        debug_system.draw(surface)
        # Not: Çizim sonucunu test etmek zor olduğundan,
        # sadece çağrının hata vermeden tamamlandığını kontrol ediyoruz 