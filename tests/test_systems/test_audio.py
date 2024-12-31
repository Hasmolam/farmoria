import pytest
from unittest.mock import MagicMock, patch
from engine.systems.audio import AudioSystem

@pytest.fixture
def audio_system():
    """AudioSystem fixture'ı"""
    with patch('pygame.mixer.init') as mock_init:
        system = AudioSystem()
        mock_init.assert_called_once()
        return system

def test_audio_system_initialization(audio_system):
    """AudioSystem başlatma testi"""
    assert audio_system.music_volume == 1.0
    assert audio_system.sound_volume == 1.0
    assert len(audio_system.sounds) == 0

@patch('pygame.mixer.Sound')
def test_load_sound(mock_sound, audio_system):
    """Ses yükleme testi"""
    # Başarılı yükleme
    mock_sound.return_value = MagicMock()
    assert audio_system.load_sound("test", "test.wav")
    assert "test" in audio_system.sounds
    
    # Başarısız yükleme
    mock_sound.side_effect = Exception("Test error")
    assert not audio_system.load_sound("error", "error.wav")
    assert "error" not in audio_system.sounds

def test_volume_control(audio_system):
    """Ses seviyesi kontrolü testi"""
    # Müzik ses seviyesi
    audio_system.set_music_volume(0.5)
    assert audio_system.get_music_volume() == 0.5
    
    # Ses efektleri ses seviyesi
    audio_system.set_sound_volume(0.7)
    assert audio_system.get_sound_volume() == 0.7
    
    # Sınırlar
    audio_system.set_music_volume(1.5)  # Max 1.0
    assert audio_system.get_music_volume() == 1.0
    
    audio_system.set_sound_volume(-0.5)  # Min 0.0
    assert audio_system.get_sound_volume() == 0.0

@patch('pygame.mixer.music')
def test_music_control(mock_music, audio_system):
    """Müzik kontrolü testi"""
    # Müzik çalma
    audio_system.play_music("test.mp3")
    mock_music.load.assert_called_once_with("test.mp3")
    mock_music.play.assert_called_once()
    
    # Müzik duraklatma
    audio_system.pause_music()
    mock_music.pause.assert_called_once()
    
    # Müzik devam ettirme
    audio_system.unpause_music()
    mock_music.unpause.assert_called_once()
    
    # Müzik durdurma
    audio_system.stop_music()
    mock_music.fadeout.assert_called_once()

@patch('pygame.mixer.Sound')
def test_sound_playback(mock_sound, audio_system):
    """Ses efekti çalma testi"""
    # Ses efekti oluştur
    mock_sound_obj = MagicMock()
    mock_sound.return_value = mock_sound_obj
    
    # Ses efekti yükle
    audio_system.load_sound("test", "test.wav")
    
    # Ses efekti çal
    audio_system.play_sound("test")
    mock_sound_obj.play.assert_called_once()
    
    # Ses efekti durdur
    audio_system.stop_sound("test")
    mock_sound_obj.stop.assert_called_once()

@patch('pygame.mixer.quit')
@patch('pygame.mixer.music.stop')
def test_cleanup(mock_stop, mock_quit, audio_system):
    """Temizleme testi"""
    audio_system.cleanup()
    mock_stop.assert_called_once()
    mock_quit.assert_called_once() 