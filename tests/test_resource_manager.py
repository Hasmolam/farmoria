import unittest
import os
import pygame
import json
import yaml
import tempfile
import numpy as np
import time
from engine import ResourceManager, AssetType
from engine.resource_manager import ImageFormat, AudioFormat, CompressionType

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak hazırlık fonksiyonu"""
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.resource_manager = ResourceManager.get_instance()
        self.resource_manager.reset()  # Her test öncesi sıfırla
        
        # Geçici test dosyaları oluştur
        self.temp_dir = tempfile.mkdtemp()
        
        # Test texture dosyası oluştur
        self.test_surface = pygame.Surface((100, 100))
        self.test_surface.fill((255, 0, 0))
        self.texture_path = os.path.join(self.temp_dir, "test_texture.png")
        pygame.image.save(self.test_surface, self.texture_path)
        
        # Test ses dosyası oluştur (1 saniyelik sinüs dalgası)
        self.sound_path = os.path.join(self.temp_dir, "test_sound.wav")
        pygame.mixer.init(44100, -16, 2, 2048)
        sample_rate = 44100
        duration = 1  # saniye
        t = np.linspace(0, duration, int(sample_rate * duration))
        samples = np.sin(2 * np.pi * 440 * t)  # 440 Hz sinüs dalgası
        scaled = np.int16(samples * 32767)
        from scipy.io import wavfile
        wavfile.write(self.sound_path, sample_rate, scaled)
    
    def tearDown(self):
        """Her test sonrası çalışacak temizlik fonksiyonu"""
        pygame.quit()
        # Geçici dosyaları temizle
        try:
            for file in [self.texture_path, self.sound_path]:
                if os.path.exists(file):
                    os.remove(file)
            os.rmdir(self.temp_dir)
        except OSError:
            pass  # Dosya silme hatalarını görmezden gel
        
        # ResourceManager'ı sıfırla
        self.resource_manager.reset()
    
    def test_singleton(self):
        """Singleton pattern testi"""
        rm1 = ResourceManager.get_instance()
        rm2 = ResourceManager.get_instance()
        self.assertIs(rm1, rm2)
    
    def test_texture_loading(self):
        """Texture yükleme testi"""
        # Texture yükle
        texture = self.resource_manager.load_texture("test_texture", self.texture_path)
        self.assertIsNotNone(texture)
        self.assertIsInstance(texture, pygame.Surface)
        
        # Önbellekten yükle ve kullanım sayısını artır
        cached_texture = self.resource_manager.load_texture("test_texture")
        self.assertEqual(texture, cached_texture)
        
        # Kaynak bilgilerini kontrol et
        info = self.resource_manager.get_resource_info("test_texture", "texture")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "test_texture")
        self.assertEqual(info["type"], "texture")
        self.assertGreater(info["size"], 0)
        self.assertGreaterEqual(info["use_count"], 1)  # En az 1 kez kullanılmış olmalı
    
    def test_sound_loading(self):
        """Ses dosyası yükleme testi"""
        # Ses yükle
        sound = self.resource_manager.load_sound("test_sound", self.sound_path)
        self.assertIsNotNone(sound)
        self.assertIsInstance(sound, pygame.mixer.Sound)
        
        # Önbellekten yükle ve kullanım sayısını artır
        cached_sound = self.resource_manager.load_sound("test_sound")
        self.assertEqual(sound, cached_sound)
        
        # Kaynak bilgilerini kontrol et
        info = self.resource_manager.get_resource_info("test_sound", "sound")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "test_sound")
        self.assertEqual(info["type"], "sound")
        self.assertGreater(info["size"], 0)
        self.assertGreaterEqual(info["use_count"], 1)  # En az 1 kez kullanılmış olmalı
    
    def test_garbage_collection(self):
        """Garbage collection testi"""
        # Bellek limitini düşür
        original_limit = self.resource_manager.memory_limit
        self.resource_manager.memory_limit = 0.1  # 100KB
        
        try:
            # Birkaç texture yükle
            for i in range(5):
                texture = pygame.Surface((100, 100))
                path = os.path.join(self.temp_dir, f"test_texture_{i}.png")
                pygame.image.save(texture, path)
                self.resource_manager.load_texture(f"texture_{i}", path)
            
            # GC'yi zorla çalıştır
            self.resource_manager._run_garbage_collection()
            
            # Bellek kullanımı kontrolü
            self.assertLessEqual(
                self.resource_manager.get_memory_usage(),
                self.resource_manager.memory_limit
            )
        finally:
            # Bellek limitini eski haline getir
            self.resource_manager.memory_limit = original_limit
    
    def test_resource_aging(self):
        """Kaynak yaşlandırma testi"""
        # Texture yükle
        texture = self.resource_manager.load_texture("test_texture", self.texture_path)
        self.assertIsNotNone(texture)
        
        # Kaynağın yaşını simüle et
        key = next(iter(self.resource_manager._resources.keys()))
        self.resource_manager._resources[key].last_used = time.time() - 400  # 5 dakikadan eski
        
        # Kullanılmayan kaynakları temizle
        self.resource_manager.clear_unused_resources(max_age=300)  # 5 dakika
        
        # Kaynağın temizlendiğini kontrol et
        self.assertEqual(self.resource_manager.get_resource_count(), 0)
    
    def test_memory_tracking(self):
        """Bellek kullanımı takibi testi"""
        # Önce tüm kaynakları temizle
        self.resource_manager.reset()
        initial_usage = self.resource_manager.get_memory_usage()
        self.assertEqual(initial_usage, 0)  # Başlangıçta bellek kullanımı 0 olmalı
        
        # Texture yükle
        texture = self.resource_manager.load_texture("test_texture", self.texture_path)
        self.assertIsNotNone(texture)
        
        # Bellek kullanımının arttığını kontrol et
        current_usage = self.resource_manager.get_memory_usage()
        self.assertGreater(current_usage, 0)
        
        # Kaynağı temizle
        self.resource_manager.reset()
        
        # Bellek kullanımının sıfırlandığını kontrol et
        final_usage = self.resource_manager.get_memory_usage()
        self.assertEqual(final_usage, 0)
    
    def test_asset_directories(self):
        """Kaynak dizinlerinin oluşturulduğunu test et."""
        rm = ResourceManager.get_instance()
        
        # Tüm dizinlerin var olduğunu kontrol et
        self.assertTrue(os.path.exists("assets"))
        self.assertTrue(os.path.exists("assets/textures"))
        self.assertTrue(os.path.exists("assets/sounds"))
        self.assertTrue(os.path.exists("assets/shaders"))
        self.assertTrue(os.path.exists("assets/maps"))
        self.assertTrue(os.path.exists("assets/fonts"))
        self.assertTrue(os.path.exists("assets/configs"))
    
    def test_map_loading(self):
        """Harita yükleme fonksiyonunu test et."""
        rm = ResourceManager.get_instance()
        
        # Test harita dosyası oluştur
        os.makedirs("assets/maps", exist_ok=True)
        test_map = """[metadata]
name: Test Level
type: test

[tiles]
........
...##...
...@#...
...##...
........"""
        
        with open("assets/maps/test_level.map", "w") as f:
            f.write(test_map)
        
        # Haritayı yükle
        map_data = rm.load_map("test_level")
        
        # Sonuçları kontrol et
        self.assertIsNotNone(map_data)
        self.assertEqual(map_data["metadata"]["name"], "Test Level")
        self.assertEqual(map_data["metadata"]["type"], "test")
        self.assertEqual(len(map_data["layers"]), 1)
        self.assertEqual(len(map_data["layers"][0]), 5)  # 5 satır
        self.assertEqual("".join(map_data["layers"][0][2]), "...@#...")  # 3. satır
    
    def test_asset_path_resolution(self):
        """Kaynak yolu çözümlemeyi test et."""
        rm = ResourceManager.get_instance()
        
        # Test dosyaları oluştur
        os.makedirs("assets/textures", exist_ok=True)
        os.makedirs("assets/sounds", exist_ok=True)
        
        # Test texture dosyası
        with open("assets/textures/player.png", "wb") as f:
            f.write(b"fake png data")
        
        # Test ses dosyası
        with open("assets/sounds/jump.wav", "wb") as f:
            f.write(b"fake wav data")
        
        # Yol çözümlemeyi test et
        texture_path = rm.get_asset_path("player", AssetType.TEXTURE)
        sound_path = rm.get_asset_path("jump", AssetType.SOUND)
        
        self.assertTrue(texture_path.endswith("player.png"))
        self.assertTrue(sound_path.endswith("jump.wav"))
        self.assertTrue(os.path.exists(texture_path))
        self.assertTrue(os.path.exists(sound_path))
    
    def tearDown(self):
        """Test sonrası temizlik."""
        super().tearDown()
        
        # Test dizinlerini temizle
        import shutil
        if os.path.exists("assets"):
            shutil.rmtree("assets")
    
    def test_memory_tracking_detailed(self):
        """Detaylı bellek kullanımı takibi testi."""
        rm = ResourceManager.get_instance()
        rm.reset()  # Belleği tamamen temizle
        
        # Başlangıç durumunu kontrol et
        stats = rm.get_memory_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["peak"], 0)
        
        # Texture yükle
        texture = rm.load_texture("test_texture", self.texture_path)
        self.assertIsNotNone(texture)
        
        # Bellek kullanımını kontrol et
        stats = rm.get_memory_stats()
        self.assertGreater(stats["total"], 0)
        self.assertGreater(stats["by_type"][AssetType.TEXTURE], 0)
        self.assertEqual(stats["by_type"][AssetType.SOUND], 0)  # Ses yüklenmedi
        
        # Ses dosyası yükle
        sound = rm.load_sound("test_sound", self.sound_path)
        self.assertIsNotNone(sound)
        
        # Güncellenmiş bellek kullanımını kontrol et
        new_stats = rm.get_memory_stats()
        self.assertGreater(new_stats["total"], stats["total"])
        self.assertGreater(new_stats["by_type"][AssetType.SOUND], 0)
        
        # Geçmiş verilerini kontrol et
        self.assertGreater(len(new_stats["history"]), 0)
        self.assertEqual(new_stats["peak"], new_stats["total"])
    
    def test_streaming_sound(self):
        """Büyük ses dosyalarının stream edilmesi testi."""
        rm = ResourceManager.get_instance()
        rm.reset()  # Belleği tamamen temizle
        
        # Büyük ses dosyası oluştur (100MB)
        large_sound_path = os.path.join(self.temp_dir, "large_sound.wav")
        sample_rate = 44100
        duration = 300  # 5 dakika
        t = np.linspace(0, duration, int(sample_rate * duration))
        samples = np.sin(2 * np.pi * 440 * t)  # 440 Hz sinüs dalgası
        scaled = np.int16(samples * 32767)
        from scipy.io import wavfile
        wavfile.write(large_sound_path, sample_rate, scaled)
        
        # Streaming threshold'u düşür
        original_threshold = rm.streaming_threshold
        rm.streaming_threshold = 10  # 10MB
        
        try:
            # Stream modunda yükle
            sound = rm.load_streaming_sound("large_sound", large_sound_path)
            self.assertIsNotNone(sound)
            
            # Streaming resource'un oluşturulduğunu kontrol et
            self.assertIn("large_sound", rm._streaming_resources)
            
            # Bellek kullanımını kontrol et
            stats = rm.get_memory_stats()
            self.assertLess(stats["by_type"][AssetType.SOUND], 60)  # 60MB'dan az olmalı
            
            # Stream'i durdur
            if "large_sound" in rm._streaming_resources:
                rm._streaming_resources["large_sound"].stop_streaming()
                del rm._streaming_resources["large_sound"]
        finally:
            # Threshold'u eski haline getir
            rm.streaming_threshold = original_threshold
            
            # Dosyayı temizle
            if os.path.exists(large_sound_path):
                os.remove(large_sound_path)
    
    def test_memory_limit_enforcement(self):
        """Bellek limiti kontrolü testi."""
        rm = ResourceManager.get_instance()
        rm.reset()  # Belleği tamamen temizle
        
        # Bellek limitini düşür
        original_limit = rm.memory_limit
        rm.memory_limit = 0.2  # 200KB
        
        try:
            # Birkaç büyük texture yükle
            textures = []
            for i in range(10):
                # 100x100 texture yaklaşık 40KB
                texture = pygame.Surface((100, 100))
                texture.fill((255, i*20, 0))  # Farklı renkler
                path = os.path.join(self.temp_dir, f"test_texture_{i}.png")
                pygame.image.save(texture, path)
                loaded = rm.load_texture(f"texture_{i}", path)
                if loaded:
                    textures.append(loaded)
            
            # Bellek kullanımının limiti aşmadığını kontrol et
            stats = rm.get_memory_stats()
            self.assertLessEqual(stats["total"], rm.memory_limit)
            
            # En az bir texture'ın yüklendiğini kontrol et
            self.assertGreater(len(textures), 0)
            
            # GC'nin çalıştığını kontrol et
            self.assertLessEqual(len(rm._resources), 5)  # En fazla 5 texture tutulabilmeli
        finally:
            # Bellek limitini eski haline getir
            rm.memory_limit = original_limit
    
    def test_image_compression(self):
        """Görsel sıkıştırma testi."""
        rm = ResourceManager()
        
        # Test görüntüsü oluştur (büyük boyutlu)
        image = pygame.Surface((512, 512))
        image.fill((255, 0, 0))  # Kırmızı
        test_file = "test_image.png"
        pygame.image.save(image, test_file)
        
        # Farklı formatlar ve sıkıştırmalar için test
        formats = [ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.WEBP]
        compressions = [CompressionType.ZLIB, CompressionType.LZ4, CompressionType.GZIP]
        
        for fmt in formats:
            for comp in compressions:
                compressed_path = rm.compress_resource(test_file, fmt, comp)
                self.assertTrue(os.path.exists(compressed_path))
                self.assertLess(os.path.getsize(compressed_path),
                              os.path.getsize(test_file))
                os.remove(compressed_path)
        
        # Temizlik
        os.remove(test_file)
    
    def test_audio_compression(self):
        """Ses sıkıştırma testi."""
        rm = ResourceManager()
        
        # Test ses dosyası oluştur
        test_data = b"Test audio data" * 1000
        test_file = "test_audio.wav"
        with open(test_file, "wb") as f:
            f.write(test_data)
        
        # Farklı formatlar ve sıkıştırmalar için test
        formats = [AudioFormat.OGG, AudioFormat.MP3]
        compressions = [CompressionType.ZLIB, CompressionType.LZ4, CompressionType.GZIP]
        
        for fmt in formats:
            for comp in compressions:
                compressed_path = rm.compress_resource(test_file, fmt, comp)
                self.assertTrue(os.path.exists(compressed_path))
                self.assertLess(os.path.getsize(compressed_path),
                              os.path.getsize(test_file))
                os.remove(compressed_path)
        
        # Temizlik
        os.remove(test_file)
    
    def test_auto_compression(self):
        """Otomatik sıkıştırma testi."""
        rm = ResourceManager()
        
        # Test dosyası oluştur
        test_data = b"Test verisi" * 1000  # Büyük veri
        test_file = "test_auto.dat"
        with open(test_file, "wb") as f:
            f.write(test_data)
        
        # Sıkıştırma yap
        compressed_path = rm.compress_resource(test_file)
        
        # Kontroller
        self.assertTrue(os.path.exists(compressed_path))
        self.assertLess(os.path.getsize(compressed_path), 
                       os.path.getsize(test_file))
        
        # Temizlik
        os.remove(test_file)
        os.remove(compressed_path)

if __name__ == '__main__':
    unittest.main() 