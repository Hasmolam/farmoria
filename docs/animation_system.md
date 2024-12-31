# Animation System

Animation System, 2D oyunlar için gelişmiş iskelet animasyon sistemi sunar. Kemik tabanlı animasyonlar, sprite animasyonları ve interpolasyon desteği içerir.

## Temel Bileşenler

### Bone (Kemik)

```python
bone = Bone(
    name="arm",
    parent=shoulder_bone,
    length=32.0,
    angle=math.radians(45)
)
```

#### Özellikler
- `name`: Kemik adı
- `parent`: Üst kemik referansı
- `length`: Kemik uzunluğu
- `angle`: Dönüş açısı (radyan)
- `scale`: Ölçek faktörü
- `position`: Konum
- `children`: Alt kemikler
- `sprite`: Bağlı sprite
- `sprite_offset`: Sprite offset'i

### Animation (Animasyon)

```python
animation = Animation("walk", duration=1.0)
animation.add_keyframe(0.0, {
    "leg_left": (0, 0, 0),
    "leg_right": (0, 0, math.pi/4)
})
```

#### Özellikler
- `name`: Animasyon adı
- `duration`: Süre (saniye)
- `keyframes`: Anahtar kareler
- `is_playing`: Oynatma durumu
- `is_looping`: Döngü durumu
- `current_time`: Geçen süre

### Skeleton (İskelet)

```python
skeleton = Skeleton()
skeleton.add_bone("torso", length=50)
skeleton.add_bone("arm_left", length=30, parent="torso")
```

#### Özellikler
- `bones`: Kemik koleksiyonu
- `root_bones`: Kök kemikler
- `animations`: Animasyon koleksiyonu
- `current_animation`: Aktif animasyon

## Temel Kullanım

### İskelet Oluşturma

```python
# İskelet oluştur
skeleton = Skeleton()

# Kemikleri ekle
skeleton.add_bone("torso", length=50)
skeleton.add_bone("arm_left", length=30, parent="torso")
skeleton.add_bone("arm_right", length=30, parent="torso")
skeleton.add_bone("leg_left", length=40, parent="torso")
skeleton.add_bone("leg_right", length=40, parent="torso")

# Sprite'ları bağla
skeleton.bones["arm_left"].set_sprite(arm_sprite)
skeleton.bones["arm_right"].set_sprite(arm_sprite, flip_x=True)
```

### Animasyon Oluşturma

```python
# Yürüme animasyonu oluştur
walk = Animation("walk", duration=1.0)

# Anahtar kareler ekle
walk.add_keyframe(0.0, {
    "leg_left": (0, 0, 0),
    "leg_right": (0, 0, math.pi/4)
})

walk.add_keyframe(0.5, {
    "leg_left": (0, 0, -math.pi/4),
    "leg_right": (0, 0, 0)
})

# İskelete animasyonu ekle
skeleton.add_animation(walk)
```

### Animasyon Oynatma

```python
# Animasyonu başlat
skeleton.play_animation("walk", loop=True)

# Ana döngüde güncelle
def update(dt):
    skeleton.update(dt)
    skeleton.draw(screen)
```

## Gelişmiş Özellikler

### Animasyon Geçişleri

```python
# Yumuşak geçiş ile animasyon değiştir
skeleton.transition_to("run", duration=0.3)
```

### İnterpolasyon Tipleri

```python
# Doğrusal interpolasyon
animation.set_interpolation(InterpolationType.LINEAR)

# Ease-in-out interpolasyon
animation.set_interpolation(InterpolationType.EASE_IN_OUT)
```

### Olay Sistemi

```python
# Animasyon olaylarını dinle
def on_animation_complete(anim_name):
    print(f"{anim_name} tamamlandı!")

skeleton.on_animation_complete = on_animation_complete
```

## Performans Optimizasyonu

1. Kemik Hiyerarşisi
   - Kemik sayısını minimize edin
   - Derin hiyerarşilerden kaçının
   - Simetrik kemikler için sprite çevirme kullanın

2. Animasyon Önbelleği
   - Sık kullanılan pozları önbellekleyin
   - Dönüşüm matrislerini yeniden kullanın
   - Anahtar kare sayısını optimize edin

3. Sprite Atlası
   - İlişkili sprite'ları atlas içinde gruplayın
   - UV koordinatlarını önbellekleyin
   - Sprite boyutlarını güç 2 değerlerine ayarlayın

## Hata Ayıklama

```python
# Debug görselleştirme
skeleton.draw_debug(screen, show_bones=True, show_joints=True)

# Performans metrikleri
stats = skeleton.get_performance_stats()
print(f"Kemik sayısı: {stats['bone_count']}")
print(f"Matris hesaplamaları: {stats['matrix_calculations']}")
```

## En İyi Uygulamalar

1. İskelet Tasarımı
   - Minimum kemik sayısı kullanın
   - Mantıklı isimlendirme yapın
   - Simetriyi koruyun

2. Animasyon Tasarımı
   - Anahtar kareleri stratejik noktalara yerleştirin
   - Doğal hareket için ease-in-out kullanın
   - Döngüsel animasyonları sorunsuz birleştirin

3. Performans
   - Gereksiz güncellemelerden kaçının
   - Görünür olmayan iskeletleri güncellemekten kaçının
   - Dönüşüm matrislerini önbellekleyin 