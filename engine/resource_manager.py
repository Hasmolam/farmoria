from typing import Dict, Any, Optional, Union, Callable
import os
import json
import yaml
import pygame
import weakref
from pathlib import Path
import importlib.util
import threading
import queue
import asyncio
import time
import gzip
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto

class ResourceKey:
    """Kaynak anahtarı sınıfı."""
    def __init__(self, name: str, resource_type: str):
        self.name = name
        self.resource_type = resource_type
        self.last_used = time.time()
        self.use_count = 1  # Başlangıçta 1 (ilk yükleme)
    
    def __hash__(self):
        return hash((self.name, self.resource_type))
    
    def __eq__(self, other):
        if not isinstance(other, ResourceKey):
            return False
        return self.name == other.name and self.resource_type == other.resource_type

class Resource:
    """Kaynak sınıfı."""
    def __init__(self, key: ResourceKey, data: Any, size: float = 0):
        self.key = key
        self.data = data
        self.size = size  # MB cinsinden
        self.last_used = time.time()
    
    def use(self):
        """Kaynağı kullan."""
        self.last_used = time.time()
        self.key.last_used = time.time()
        self.key.use_count += 1
        return self.data

class ResourceRequest:
    """Kaynak yükleme isteği sınıfı."""
    def __init__(self, key: ResourceKey, callback: Optional[Callable] = None, **kwargs):
        self.key = key
        self.callback = callback
        self.kwargs = kwargs
        self.result = None
        self.error = None
        self.is_complete = False

class AssetType:
    """Kaynak türleri."""
    TEXTURE = "texture"
    SOUND = "sound"
    SHADER = "shader"
    MAP = "map"
    FONT = "font"
    CONFIG = "config"

class AssetPath:
    """Kaynak dizin yapısı."""
    def __init__(self, base_path: str = "assets"):
        self.base = base_path
        self.textures = os.path.join(base_path, "textures")
        self.sounds = os.path.join(base_path, "sounds")
        self.shaders = os.path.join(base_path, "shaders")
        self.maps = os.path.join(base_path, "maps")
        self.fonts = os.path.join(base_path, "fonts")
        self.configs = os.path.join(base_path, "configs")
    
    def create_directories(self):
        """Gerekli dizinleri oluştur."""
        for path in [self.base, self.textures, self.sounds, 
                    self.shaders, self.maps, self.fonts, self.configs]:
            os.makedirs(path, exist_ok=True)
    
    def get_path(self, asset_type: str) -> str:
        """Belirtilen kaynak türü için dizin yolunu döndür."""
        paths = {
            AssetType.TEXTURE: self.textures,
            AssetType.SOUND: self.sounds,
            AssetType.SHADER: self.shaders,
            AssetType.MAP: self.maps,
            AssetType.FONT: self.fonts,
            AssetType.CONFIG: self.configs
        }
        return paths.get(asset_type, self.base)

class MemoryUsageTracker:
    """Bellek kullanımını takip eden sınıf."""
    def __init__(self):
        self.total_usage = 0  # Toplam bellek kullanımı (MB)
        self.usage_by_type = {  # Kaynak türüne göre bellek kullanımı
            AssetType.TEXTURE: 0,
            AssetType.SOUND: 0,
            AssetType.MAP: 0,
            AssetType.SHADER: 0,
            AssetType.FONT: 0,
            AssetType.CONFIG: 0
        }
        self.peak_usage = 0  # En yüksek bellek kullanımı
        self.usage_history = []  # Bellek kullanım geçmişi
    
    def add_usage(self, size: float, resource_type: str):
        """Bellek kullanımını artır."""
        self.total_usage += size
        self.usage_by_type[resource_type] += size
        self.peak_usage = max(self.peak_usage, self.total_usage)
        self.usage_history.append((time.time(), self.total_usage))
        
        # Geçmişi son 1 saate kadar tut
        current_time = time.time()
        self.usage_history = [
            (t, u) for t, u in self.usage_history 
            if current_time - t <= 3600
        ]
    
    def remove_usage(self, size: float, resource_type: str):
        """Bellek kullanımını azalt."""
        self.total_usage = max(0, self.total_usage - size)
        self.usage_by_type[resource_type] = max(
            0, self.usage_by_type[resource_type] - size
        )
    
    def get_usage_stats(self) -> dict:
        """Bellek kullanım istatistiklerini döndür."""
        return {
            "total": self.total_usage,
            "peak": self.peak_usage,
            "by_type": self.usage_by_type.copy(),
            "history": self.usage_history.copy()
        }

class StreamingResource:
    """Büyük kaynakları stream etmek için sınıf."""
    def __init__(self, path: str, chunk_size: int = 1024 * 1024):  # 1MB chunk
        self.path = path
        self.chunk_size = chunk_size
        self.file_size = os.path.getsize(path)
        self.current_position = 0
        self.file = None
        self.is_streaming = False
        self.buffer = None
        self.buffer_position = 0
    
    def start_streaming(self):
        """Stream'i başlat."""
        if not self.is_streaming:
            self.file = open(self.path, 'rb')
            self.is_streaming = True
            self.buffer = self._read_chunk()
    
    def stop_streaming(self):
        """Stream'i durdur."""
        if self.is_streaming:
            self.file.close()
            self.file = None
            self.is_streaming = False
            self.buffer = None
            self.current_position = 0
            self.buffer_position = 0
    
    def _read_chunk(self) -> bytes:
        """Bir sonraki chunk'ı oku."""
        chunk = self.file.read(self.chunk_size)
        self.current_position = self.file.tell()
        return chunk
    
    def read(self, size: int) -> bytes:
        """Belirtilen boyutta veri oku."""
        if not self.is_streaming:
            self.start_streaming()
        
        result = bytearray()
        remaining = size
        
        while remaining > 0:
            if not self.buffer:
                self.buffer = self._read_chunk()
                self.buffer_position = 0
                if not self.buffer:  # EOF
                    break
            
            # Buffer'dan veri oku
            available = len(self.buffer) - self.buffer_position
            to_read = min(remaining, available)
            result.extend(self.buffer[self.buffer_position:self.buffer_position + to_read])
            self.buffer_position += to_read
            remaining -= to_read
            
            # Buffer tükendiyse yeni chunk oku
            if self.buffer_position >= len(self.buffer):
                self.buffer = None
        
        return bytes(result)
    
    def seek(self, position: int):
        """Dosyada belirtilen pozisyona git."""
        if not self.is_streaming:
            self.start_streaming()
        
        self.file.seek(position)
        self.current_position = position
        self.buffer = None
        self.buffer_position = 0

class CompressionType(Enum):
    ZLIB = auto()
    LZ4 = auto()
    GZIP = auto()

class ImageFormat(Enum):
    PNG = auto()
    JPEG = auto() 
    WEBP = auto()

class AudioFormat(Enum):
    OGG = auto()
    MP3 = auto()
    WAV = auto()

class ResourceCompressor:
    """Kaynak sıkıştırma ve açma işlemleri için sınıf."""
    def __init__(self):
        self.compression_level = 6  # Varsayılan sıkıştırma seviyesi (1-9)
        self._cache = {}  # Sıkıştırılmış veri önbelleği
    
    def compress_image(self, image: pygame.Surface, format: str = ImageFormat.PNG,
                      compression: str = CompressionType.ZLIB) -> bytes:
        """Görsel verilerini sıkıştır."""
        import io
        import zlib
        import lz4.frame
        
        # Görüntüyü belleğe kaydet
        buffer = io.BytteIO()
        if format == ImageFormat.PNG:
            pygame.image.save(image, buffer, "PNG")
        elif format == ImageFormat.JPEG:
            pygame.image.save(image, buffer, "JPEG")
        elif format == ImageFormat.WEBP:
            from PIL import Image
            pil_image = Image.frombytes("RGBA", image.get_size(), 
                                      pygame.image.tostring(image, "RGBA"))
            pil_image.save(buffer, "WEBP", quality=85)
        
        data = buffer.getvalue()
        
        # Sıkıştırma uygula
        if compression == CompressionType.ZLIB:
            return zlib.compress(data, self.compression_level)
        elif compression == CompressionType.LZ4:
            return lz4.frame.compress(data)
        elif compression == CompressionType.GZIP:
            import gzip
            gz_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=gz_buffer, mode='wb', 
                             compresslevel=self.compression_level) as gz:
                gz.write(data)
            return gz_buffer.getvalue()
        
        return data
    
    def decompress_image(self, data: bytes, compression: str = CompressionType.ZLIB) -> pygame.Surface:
        """Sıkıştırılmış görsel verilerini aç."""
        import io
        import zlib
        import lz4.frame
        
        # Önbellekte varsa döndür
        cache_key = hash(data)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Sıkıştırmayı aç
        if compression == CompressionType.ZLIB:
            decompressed = zlib.decompress(data)
        elif compression == CompressionType.LZ4:
            decompressed = lz4.frame.decompress(data)
        elif compression == CompressionType.GZIP:
            gz_buffer = io.BytesIO(data)
            with gzip.GzipFile(fileobj=gz_buffer, mode='rb') as gz:
                decompressed = gz.read()
        else:
            decompressed = data
        
        # Görüntüyü yükle
        buffer = io.BytesIO(decompressed)
        image = pygame.image.load(buffer)
        
        # Önbelleğe al
        self._cache[cache_key] = image
        return image
    
    def compress_audio(self, audio_data: bytes, format: str = AudioFormat.OGG,
                      compression: str = CompressionType.ZLIB) -> bytes:
        """Ses verilerini sıkıştır."""
        import io
        import zlib
        import lz4.frame
        from pydub import AudioSegment
        
        # Ses verilerini yükle
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Hedef formata dönüştür
        buffer = io.BytesIO()
        if format == AudioFormat.OGG:
            audio.export(buffer, format="ogg", codec="libvorbis", 
                        parameters=["-q:a", "4"])  # Kalite seviyesi
        elif format == AudioFormat.MP3:
            audio.export(buffer, format="mp3", codec="libmp3lame",
                        parameters=["-q:a", "2"])  # Kalite seviyesi
        
        data = buffer.getvalue()
        
        # Sıkıştırma uygula
        if compression == CompressionType.ZLIB:
            return zlib.compress(data, self.compression_level)
        elif compression == CompressionType.LZ4:
            return lz4.frame.compress(data)
        elif compression == CompressionType.GZIP:
            gz_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=gz_buffer, mode='wb',
                             compresslevel=self.compression_level) as gz:
                gz.write(data)
            return gz_buffer.getvalue()
        
        return data
    
    def decompress_audio(self, data: bytes, compression: str = CompressionType.ZLIB) -> bytes:
        """Sıkıştırılmış ses verilerini aç."""
        import io
        import zlib
        import lz4.frame
        
        # Önbellekte varsa döndür
        cache_key = hash(data)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Sıkıştırmayı aç
        if compression == CompressionType.ZLIB:
            decompressed = zlib.decompress(data)
        elif compression == CompressionType.LZ4:
            decompressed = lz4.frame.decompress(data)
        elif compression == CompressionType.GZIP:
            gz_buffer = io.BytesIO(data)
            with gzip.GzipFile(fileobj=gz_buffer, mode='rb') as gz:
                decompressed = gz.read()
        else:
            decompressed = data
        
        # Önbelleğe al
        self._cache[cache_key] = decompressed
        return decompressed
    
    def compress_file(self, input_path: str, output_path: str):
        """Dosyayı sıkıştır ve belirtilen yola kaydet."""
        import gzip
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
    
    def compress_file_gzip(self, input_path: str, output_path: str):
        """GZIP sıkıştırması uygula."""
        import gzip
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
    
    def compress_file_zlib(self, input_path: str, output_path: str):
        """ZLIB sıkıştırması uygula."""
        import zlib
        with open(input_path, 'rb') as f_in:
            data = f_in.read()
            compressed = zlib.compress(data)
            with open(output_path, 'wb') as f_out:
                f_out.write(compressed)
    
    def compress_file_lz4(self, input_path: str, output_path: str):
        """LZ4 sıkıştırması uygula."""
        import lz4.frame
        with open(input_path, 'rb') as f_in:
            data = f_in.read()
            compressed = lz4.frame.compress(data)
            with open(output_path, 'wb') as f_out:
                f_out.write(compressed)

class ResourceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._resources: Dict[ResourceKey, Resource] = {}
            
            # Bellek yönetimi
            self.memory_limit = 1024  # 1 GB
            self.streaming_threshold = 50  # 50 MB üzeri kaynakları stream et
            self.memory_tracker = MemoryUsageTracker()
            
            # Sıkıştırma ayarları
            self.compressor = ResourceCompressor()
            self.default_image_format = ImageFormat.PNG
            self.default_audio_format = AudioFormat.OGG
            self.default_compression = CompressionType.ZLIB
            self.auto_compress = True  # Otomatik sıkıştırma
            
            # Streaming kaynaklar
            self._streaming_resources: Dict[str, StreamingResource] = {}
            
            # Zayıf referanslar için havuz
            self._resource_pool = weakref.WeakValueDictionary()
            
            # Asenkron yükleme için iş parçacığı havuzu
            self._thread_pool = ThreadPoolExecutor(max_workers=4)
            self._loading_queue = queue.Queue()
            self._loading_thread = threading.Thread(target=self._process_loading_queue, daemon=True)
            self._loading_thread.start()
            
            # Garbage collection için ayarlar
            self.gc_interval = 60  # 60 saniye
            self.gc_threshold = 0.8  # Bellek kullanımı %80'i aştığında GC başlat
            self.last_gc_time = time.time()
            
            # GC thread'ini başlat
            self._gc_thread = threading.Thread(target=self._gc_loop, daemon=True)
            self._gc_thread.start()
            
            # Dosya sistemi yapısı
            self.asset_paths = AssetPath()
            self.asset_paths.create_directories()
    
    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        """Singleton instance'ı döndür."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def reset(self):
        """Test için instance'ı sıfırla."""
        # Streaming kaynakları temizle
        for name, resource in list(self._streaming_resources.items()):
            resource.stop_streaming()
        self._streaming_resources.clear()
        
        # Kaynakları temizle
        self._resources.clear()
        self._resource_pool.clear()
        self._loading_queue = queue.Queue()
        
        # Bellek kullanımını sıfırla
        self.current_memory_usage = 0
        self.memory_tracker = MemoryUsageTracker()
        
        # Ayarları varsayılana döndür
        self.memory_limit = 1024  # 1 GB
        self.streaming_threshold = 50  # 50 MB
        self.gc_threshold = 0.8
        self.gc_interval = 60
        
        # Thread'leri yeniden başlat
        if hasattr(self, '_loading_thread') and self._loading_thread.is_alive():
            self._loading_thread = threading.Thread(target=self._process_loading_queue, daemon=True)
            self._loading_thread.start()
            
        if hasattr(self, '_gc_thread') and self._gc_thread.is_alive():
            self._gc_thread = threading.Thread(target=self._gc_loop, daemon=True)
            self._gc_thread.start()
    
    def get_resource(self, name: str, resource_type: str) -> Optional[Any]:
        """Kaynağı al veya yükle."""
        key = ResourceKey(name, resource_type)
        
        # Önbellekte varsa döndür
        if key in self._resources:
            return self._resources[key].use()
        
        # Havuzda varsa döndür
        if name in self._resource_pool:
            return self._resource_pool[name]
        
        return None
    
    def get_asset_path(self, name: str, asset_type: str) -> str:
        """Kaynak için tam dosya yolunu döndür."""
        base_dir = self.asset_paths.get_path(asset_type)
        
        # Uzantıyı belirle
        extensions = {
            AssetType.TEXTURE: [".png", ".jpg", ".jpeg"],
            AssetType.SOUND: [".wav", ".ogg", ".mp3"],
            AssetType.SHADER: [".vert", ".frag", ".comp"],
            AssetType.MAP: [".map", ".level"],
            AssetType.FONT: [".ttf", ".otf"],
            AssetType.CONFIG: [".json", ".yaml"]
        }
        
        # Önce verilen isimle tam yolu dene
        if os.path.exists(os.path.join(base_dir, name)):
            return os.path.join(base_dir, name)
        
        # Desteklenen uzantılarla dene
        for ext in extensions.get(asset_type, [""]):
            path = os.path.join(base_dir, f"{name}{ext}")
            if os.path.exists(path):
                return path
        
        # Bulunamazsa orijinal yolu döndür
        return os.path.join(base_dir, name)
    
    def load_texture(self, name: str, path: str = None, lazy: bool = False,
                    async_load: bool = False, callback: Optional[Callable] = None,
                    format: str = None, compression: str = None) -> Optional[pygame.Surface]:
        """Texture yükle."""
        key = ResourceKey(name, AssetType.TEXTURE)
        
        # Format ve sıkıştırma ayarlarını belirle
        format = format or self.default_image_format
        compression = compression or self.default_compression
        
        # Önbellekte varsa döndür
        if key in self._resources:
            return self._resources[key].use()
        
        # Path belirtilmemişse, otomatik bul
        if path is None:
            path = self.get_asset_path(name, AssetType.TEXTURE)
        
        if lazy:
            request = ResourceRequest(key, callback, format=format, compression=compression)
            self._loading_queue.put((AssetType.TEXTURE, path, request))
            return None
            
        if async_load:
            request = ResourceRequest(key, callback, format=format, compression=compression)
            self._loading_queue.put((AssetType.TEXTURE, path, request))
            return None
        
        try:
            # Dosya uzantısını kontrol et
            ext = os.path.splitext(path)[1].lower()
            is_compressed = ext in [".gz", ".lz4", ".zlib"]
            
            if is_compressed:
                # Sıkıştırılmış dosyayı oku
                with open(path, "rb") as f:
                    data = f.read()
                texture = self.compressor.decompress_image(data, compression)
            else:
                # Normal dosyayı yükle
                texture = pygame.image.load(path).convert_alpha()
                
                # Otomatik sıkıştırma aktifse ve dosya büyükse sıkıştır
                if self.auto_compress:
                    size = os.path.getsize(path)
                    if size > 1024 * 1024:  # 1MB'dan büyükse
                        compressed = self.compressor.compress_image(texture, format, compression)
                        # Sıkıştırılmış versiyonu kaydet
                        compressed_path = f"{path}.{compression}"
                        with open(compressed_path, "wb") as f:
                            f.write(compressed)
            
            size = texture.get_size()
            memory_usage = size[0] * size[1] * 4 / (1024 * 1024)  # MB cinsinden
            
            # Bellek kontrolü
            if self.current_memory_usage + memory_usage > self.memory_limit:
                self._run_garbage_collection()
            
            # Hala bellek yetersizse yükleme
            if self.current_memory_usage + memory_usage > self.memory_limit:
                print(f"Bellek limiti aşıldı: {self.current_memory_usage + memory_usage} MB > {self.memory_limit} MB")
                return None
            
            self._add_resource(key, texture, memory_usage)
            return self._resources[key].use()
        except Exception as e:
            print(f"Texture yüklenirken hata: {e}")
            return None
    
    def load_sound(self, name: str, path: str = None, lazy: bool = False,
                  async_load: bool = False, callback: Optional[Callable] = None,
                  format: str = None, compression: str = None) -> Optional[pygame.mixer.Sound]:
        """Ses dosyası yükle."""
        key = ResourceKey(name, AssetType.SOUND)
        
        # Format ve sıkıştırma ayarlarını belirle
        format = format or self.default_audio_format
        compression = compression or self.default_compression
        
        # Önbellekte varsa döndür
        if key in self._resources:
            return self._resources[key].use()
        
        # Path belirtilmemişse, otomatik bul
        if path is None:
            path = self.get_asset_path(name, AssetType.SOUND)
        
        if lazy:
            request = ResourceRequest(key, callback, format=format, compression=compression)
            self._loading_queue.put((AssetType.SOUND, path, request))
            return None
            
        if async_load:
            request = ResourceRequest(key, callback, format=format, compression=compression)
            self._loading_queue.put((AssetType.SOUND, path, request))
            return None
        
        try:
            # Dosya boyutunu kontrol et
            size = os.path.getsize(path) / (1024 * 1024)  # MB cinsinden
            
            # Büyük dosyalar için streaming kullan
            if size > self.streaming_threshold:
                return self.load_streaming_sound(name, path, format, compression)
            
            # Dosya uzantısını kontrol et
            ext = os.path.splitext(path)[1].lower()
            is_compressed = ext in [".gz", ".lz4", ".zlib"]
            
            if is_compressed:
                # Sıkıştırılmış dosyayı oku
                with open(path, "rb") as f:
                    data = f.read()
                audio_data = self.compressor.decompress_audio(data, compression)
                sound = pygame.mixer.Sound(buffer=audio_data)
            else:
                # Normal dosyayı yükle
                sound = pygame.mixer.Sound(path)
                
                # Otomatik sıkıştırma aktifse ve dosya büyükse sıkıştır
                if self.auto_compress:
                    if size > 1:  # 1MB'dan büyükse
                        with open(path, "rb") as f:
                            audio_data = f.read()
                        compressed = self.compressor.compress_audio(audio_data, format, compression)
                        # Sıkıştırılmış versiyonu kaydet
                        compressed_path = f"{path}.{compression}"
                        with open(compressed_path, "wb") as f:
                            f.write(compressed)
            
            # Bellek kontrolü
            if self.current_memory_usage + size > self.memory_limit:
                self._run_garbage_collection()
            
            # Hala bellek yetersizse yükleme
            if self.current_memory_usage + size > self.memory_limit:
                return None
            
            self._add_resource(key, sound, size)
            return self._resources[key].use()
        except Exception as e:
            print(f"Ses dosyası yüklenirken hata: {e}")
            return None
    
    def load_map(self, name: str, path: str = None) -> Optional[dict]:
        """Harita dosyasını yükle."""
        key = ResourceKey(name, AssetType.MAP)
        
        # Önbellekte varsa döndür
        if key in self._resources:
            return self._resources[key].use()
        
        # Path belirtilmemişse, otomatik bul
        if path is None:
            path = self.get_asset_path(name, AssetType.MAP)
        
        try:
            # Dosya uzantısına göre yükleme yöntemini belirle
            ext = os.path.splitext(path)[1].lower()
            
            if ext == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif ext == '.yaml':
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            else:  # Özel .map veya .level formatı
                with open(path, 'r', encoding='utf-8') as f:
                    data = self._parse_map_file(f.read())
            
            size = os.path.getsize(path) / (1024 * 1024)  # MB cinsinden
            resource = Resource(key, data, size)
            self._resources[key] = resource
            self.current_memory_usage += size
            
            return resource.use()
        except Exception as e:
            print(f"Harita yüklenirken hata: {e}")
            return None
    
    def _parse_map_file(self, content: str) -> dict:
        """Özel harita formatını parse et."""
        # Örnek format:
        # [metadata]
        # name: Level 1
        # type: dungeon
        # 
        # [tiles]
        # ..........
        # ...#####..
        # ...#...#..
        # ...#.@.#..
        # ...#####..
        # ..........
        
        result = {"metadata": {}, "layers": []}
        current_section = None
        current_data = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if not line:  # Boş satır
                if current_section == "tiles" and current_data:
                    result["layers"].append(current_data)
                    current_data = []
                continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                continue
            
            if current_section == "metadata":
                key, value = line.split(':', 1)
                result["metadata"][key.strip()] = value.strip()
            elif current_section == "tiles":
                current_data.append(list(line))
        
        if current_section == "tiles" and current_data:
            result["layers"].append(current_data)
        
        return result
    
    def _gc_loop(self):
        """Garbage collection döngüsü."""
        while True:
            time.sleep(self.gc_interval)
            
            # Bellek kullanımı threshold'u aştıysa GC çalıştır
            if self.current_memory_usage > self.memory_limit * self.gc_threshold:
                self._run_garbage_collection()
    
    def _run_garbage_collection(self):
        """Garbage collection çalıştır."""
        current_time = time.time()
        target_usage = self.memory_limit * 0.7  # Hedef bellek kullanımı
        
        # Bellek kullanımı limiti aşılmışsa
        if self.current_memory_usage > target_usage:
            print(f"GC başlatıldı. Mevcut kullanım: {self.current_memory_usage} MB, Hedef: {target_usage} MB")
            
            # En az kullanılan ve en eski kaynakları bul
            resources = sorted(
                self._resources.items(),
                key=lambda x: (x[1].key.use_count, current_time - x[1].last_used)
            )
            
            # Önce kullanılmayan kaynakları temizle
            for key, resource in list(resources):
                if current_time - resource.last_used > 300:  # 5 dakika
                    print(f"Kullanılmayan kaynak temizlendi: {key.name}")
                    self._remove_resource(key)
                    resources = [r for r in resources if r[0] != key]
                    
                    if self.current_memory_usage <= target_usage:
                        print(f"GC tamamlandı. Yeni kullanım: {self.current_memory_usage} MB")
                        return
            
            # Hala bellek limiti aşılıyorsa, en az kullanılan kaynakları temizle
            while resources and self.current_memory_usage > target_usage:
                key, resource = resources.pop(0)
                print(f"En az kullanılan kaynak temizlendi: {key.name}")
                self._remove_resource(key)
            
            print(f"GC tamamlandı. Yeni kullanım: {self.current_memory_usage} MB")
    
    def clear_unused_resources(self, max_age: float = 300):
        """Belirli bir süredir kullanılmayan kaynakları temizle."""
        current_time = time.time()
        
        # Kullanılan kaynakları tekrar hesapla
        resources_to_keep = {}
        self.current_memory_usage = 0  # Bellek kullanımını sıfırla
        
        for key, resource in list(self._resources.items()):
            if current_time - resource.last_used <= max_age:
                resources_to_keep[key] = resource
                self.current_memory_usage += resource.size
        
        # Kaynakları güncelle
        self._resources = resources_to_keep
    
    def get_resource_info(self, name: str, resource_type: str) -> Optional[dict]:
        """Kaynak bilgilerini döndür."""
        key = ResourceKey(name, resource_type)
        
        if key in self._resources:
            resource = self._resources[key]
            return {
                "name": key.name,
                "type": key.resource_type,
                "size": resource.size,
                "last_used": resource.last_used,
                "use_count": key.use_count
            }
        
        return None
    
    def get_memory_usage(self) -> float:
        """Toplam bellek kullanımını döndür (MB)."""
        return self.current_memory_usage
    
    def get_resource_count(self) -> int:
        """Toplam kaynak sayısını döndür."""
        return len(self._resources)
    
    def _process_loading_queue(self):
        """Yükleme kuyruğundaki istekleri işler."""
        while True:
            try:
                resource_type, path, request = self._loading_queue.get()
                try:
                    if resource_type == "texture":
                        result = self.load_texture(request.key.name, path)
                    elif resource_type == "sound":
                        result = self.load_sound(request.key.name, path)
                    request.result = result
                except Exception as e:
                    request.error = e
                finally:
                    request.is_complete = True
                    if request.callback:
                        request.callback(request)
                self._loading_queue.task_done()
            except Exception as e:
                print(f"Kaynak yükleme hatası: {e}")
                continue
    
    def load_streaming_sound(self, name: str, path: str = None) -> Optional[pygame.mixer.Sound]:
        """Büyük ses dosyasını stream et."""
        key = ResourceKey(name, AssetType.SOUND)
        
        # Path belirtilmemişse, otomatik bul
        if path is None:
            path = self.get_asset_path(name, AssetType.SOUND)
        
        try:
            # Dosya boyutunu kontrol et
            size = os.path.getsize(path) / (1024 * 1024)  # MB cinsinden
            
            print(f"Ses dosyası boyutu: {size} MB, Threshold: {self.streaming_threshold} MB")
            
            if size > self.streaming_threshold:
                print(f"Stream modu kullanılıyor: {name}")
                # Stream modunda yükle
                streaming = StreamingResource(path)
                streaming.start_streaming()
                
                # Küçük bir buffer yükle
                buffer = streaming.read(1024 * 1024)  # 1MB başlangıç buffer
                if not buffer:
                    print("Buffer okunamadı")
                    return None
                
                try:
                    sound = pygame.mixer.Sound(buffer=buffer)
                except Exception as e:
                    print(f"Ses oluşturma hatası: {e}")
                    return None
                
                # Bellek kullanımını sadece buffer kadar artır
                buffer_size = len(buffer) / (1024 * 1024)  # MB cinsinden
                self.memory_tracker.add_usage(buffer_size, AssetType.SOUND)
                
                # Streaming resource'u kaydet
                self._streaming_resources[name] = streaming
                print(f"Streaming resource kaydedildi: {name}")
                
                return sound
            else:
                print(f"Normal yükleme kullanılıyor: {name}")
                # Normal yükleme
                return self.load_sound(name, path)
        except Exception as e:
            print(f"Ses dosyası stream edilirken hata: {e}")
            if name in self._streaming_resources:
                self._streaming_resources[name].stop_streaming()
                del self._streaming_resources[name]
            return None
    
    def get_memory_stats(self) -> dict:
        """Bellek kullanım istatistiklerini döndür."""
        return self.memory_tracker.get_usage_stats()
    
    def _add_resource(self, key: ResourceKey, resource: Any, size: float):
        """Kaynağı ekle ve bellek kullanımını güncelle."""
        self._resources[key] = Resource(key, resource, size)
        self.memory_tracker.add_usage(size, key.resource_type)
        self.current_memory_usage += size
    
    def _remove_resource(self, key: ResourceKey):
        """Kaynağı kaldır ve bellek kullanımını güncelle."""
        if key in self._resources:
            resource = self._resources[key]
            self.memory_tracker.remove_usage(resource.size, key.resource_type)
            self.current_memory_usage -= resource.size
            del self._resources[key]
    
    def compress_resource(self, file_path: str, format_type=None, compression_type=CompressionType.GZIP) -> str:
        """Kaynağı sıkıştır ve sıkıştırılmış dosya yolunu döndür."""
        compressor = ResourceCompressor()
        
        # Format uzantısını belirle
        if format_type:
            format_ext = format_type.name.lower()
            output_path = f"{file_path}.{format_ext}"
            # Format dönüşümü yap
            if isinstance(format_type, ImageFormat):
                img = pygame.image.load(file_path)
                pygame.image.save(img, output_path)
            elif isinstance(format_type, AudioFormat):
                # TODO: Ses formatı dönüşümü
                output_path = file_path
        else:
            output_path = file_path
        
        # Sıkıştırma uzantısını ekle
        compressed_path = f"{output_path}.{compression_type.name.lower()}"
        
        # Sıkıştırma yap
        if compression_type == CompressionType.GZIP:
            compressor.compress_file_gzip(output_path, compressed_path)
        elif compression_type == CompressionType.ZLIB:
            compressor.compress_file_zlib(output_path, compressed_path)
        elif compression_type == CompressionType.LZ4:
            compressor.compress_file_lz4(output_path, compressed_path)
        
        # Geçici format dönüşüm dosyasını temizle
        if format_type and output_path != file_path:
            os.remove(output_path)
        
        return compressed_path
    
    # ... (Diğer metodlar aynı kalacak) ... 