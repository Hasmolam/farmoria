# Farmoria Game Engine

Modern ve modüler 2D oyun motoru.

## Modül Yapısı

Engine modülü beş ana alt modülden oluşur:

### Core
Temel motor bileşenleri:
- `base.py`: Temel sınıflar ve arayüzler
- `core.py`: Çekirdek motor fonksiyonları
- `game_state.py`: Oyun durumu yönetimi

### Graphics
Grafik ve render sistemleri:
- `renderer.py`: Ana render sistemi
- `shader_system.py`: Shader yönetimi
- `texture_atlas.py`: Doku atlası işlemleri
- `shaders/`: Shader dosyaları

### Systems
Oyun sistemleri:
- `animation.py`: Animasyon sistemi
- `audio.py`: Ses sistemi
- `physics.py`: Fizik motoru
- `input.py`: Girdi yönetimi

### Components
Oyun bileşenleri:
- `player.py`: Oyuncu yönetimi
- `scene.py`: Sahne sistemi
- `ui.py`: Kullanıcı arayüzü bileşenleri

### Utils
Yardımcı araçlar:
- `debug.py`: Hata ayıklama araçları
- `resource_manager.py`: Kaynak yönetimi
- `timing.py`: Zamanlama işlemleri
- `data_manager.py`: Veri yönetimi
- `sprite_generator.py`: Sprite oluşturma araçları
- `isometric.py`: İzometrik görünüm araçları

## Özellikler

- 🎮 Güçlü 2D Grafik Motoru
- 🎨 Modern Shader Sistemi
- 💫 İskelet Animasyon Desteği
- 📦 Akıllı Kaynak Yönetimi
- 🚀 Asenkron Yükleme Sistemi
- 🎯 Fizik Motoru Entegrasyonu

## Kurulum

```bash
pip install -r requirements.txt
```

## Hızlı Başlangıç

```python
from engine import Scene, Sprite, Animation

# Yeni bir sahne oluştur
scene = Scene(800, 600)

# Sprite ekle
sprite = Sprite("player.png")
scene.add(sprite)

# Animasyon oluştur
animation = Animation("walk")
animation.add_frame(0, {"x": 0, "y": 0})
animation.add_frame(1, {"x": 32, "y": 0})
sprite.play_animation(animation)

# Oyun döngüsü
while True:
    scene.update()
    scene.render()
```

## Modüller

### Resource Manager
Kaynak yönetim sistemi, oyun varlıklarının verimli yüklenmesi ve yönetilmesini sağlar.

### Animation System
Gelişmiş iskelet animasyon sistemi, karmaşık 2D animasyonlar oluşturmanıza olanak tanır.

### Shader System
ModernGL tabanlı shader sistemi, modern grafik efektleri oluşturmanızı sağlar.

## Örnekler

Örnek projeleri `examples/` klasöründe bulabilirsiniz:
- Basit Sprite Örneği
- İskelet Animasyon Demosu
- Shader Efektleri Demosu

## Geliştirici Dökümantasyonu

Detaylı API dökümantasyonu için `docs/` klasörüne bakın.

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

