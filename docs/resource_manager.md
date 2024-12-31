# Resource Manager

Resource Manager, oyun varlıklarının (assets) verimli bir şekilde yüklenmesi, yönetilmesi ve önbelleklenmesi için tasarlanmış bir sistemdir.

## Temel Özellikler

- Asenkron kaynak yükleme
- Akıllı önbellekleme
- Otomatik kaynak temizleme
- Bellek kullanım takibi
- Sıkıştırma desteği

## Sınıflar

### ResourceKey

Kaynak tanımlayıcı sınıfı.

```python
key = ResourceKey(name="player", resource_type="texture")
```

#### Özellikler
- `name`: Kaynak adı
- `resource_type`: Kaynak türü
- `last_used`: Son kullanım zamanı
- `use_count`: Kullanım sayısı

### Resource

Kaynak verilerini tutan sınıf.

```python
resource = Resource(key=key, data=texture_data, size=1.5)  # size in MB
```

#### Özellikler
- `key`: ResourceKey nesnesi
- `data`: Kaynak verisi
- `size`: Bellek kullanımı (MB)
- `last_used`: Son kullanım zamanı

### ResourceRequest

Kaynak yükleme isteklerini yöneten sınıf.

```python
request = ResourceRequest(
    key=key,
    callback=on_load_complete,
    priority=1
)
```

#### Özellikler
- `key`: ResourceKey nesnesi
- `callback`: Yükleme tamamlandığında çağrılacak fonksiyon
- `kwargs`: Ek parametreler

## Kullanım Örnekleri

### Temel Kullanım

```python
# Resource Manager oluştur
manager = ResourceManager()

# Texture yükle
texture_key = ResourceKey("player", AssetType.TEXTURE)
texture = await manager.load_resource(texture_key)

# Texture'ı kullan
sprite.set_texture(texture.use())

# Kaynağı temizle
manager.unload_resource(texture_key)
```

### Asenkron Yükleme

```python
async def load_game_assets():
    # Birden fazla kaynağı paralel yükle
    resources = await manager.load_resources([
        ResourceKey("player", AssetType.TEXTURE),
        ResourceKey("background", AssetType.TEXTURE),
        ResourceKey("music", AssetType.SOUND)
    ])
    
    return resources
```

### Önbellekleme Stratejisi

```python
# Önbellek boyutunu ayarla
manager.set_cache_size(1024)  # 1GB

# Öncelikli kaynakları önbellekte tut
manager.pin_resource(texture_key)

# Önbelleği temizle
manager.clear_cache()
```

### Bellek Takibi

```python
# Bellek kullanım istatistiklerini al
stats = manager.get_memory_stats()
print(f"Toplam kullanım: {stats['total_mb']}MB")
print(f"Texture kullanımı: {stats['texture_mb']}MB")
```

## Hata Yönetimi

```python
try:
    texture = await manager.load_resource(texture_key)
except ResourceLoadError as e:
    print(f"Yükleme hatası: {e}")
except ResourceNotFoundError as e:
    print(f"Kaynak bulunamadı: {e}")
```

## En İyi Uygulamalar

1. Kaynakları mümkün olduğunca asenkron yükleyin
2. Sık kullanılan kaynakları önbellekte tutun
3. Kullanılmayan kaynakları temizleyin
4. Bellek kullanımını düzenli takip edin
5. Büyük kaynaklar için streaming kullanın

## Performans İpuçları

1. Texture atlasları kullanın
2. Kaynakları gruplar halinde yükleyin
3. Önbellek boyutunu oyununuza göre optimize edin
4. Yükleme önceliklerini doğru ayarlayın
5. Sıkıştırma seviyesini dengeleyin 