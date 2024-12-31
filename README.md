# Farmoria Game Engine

Farmoria, Python tabanlı modern bir 2D oyun motorudur. ModernGL kullanarak güçlü grafik özellikleri sunar ve gelişmiş animasyon sistemleri içerir.

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

