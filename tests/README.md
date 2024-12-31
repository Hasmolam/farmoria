# Farmoria Test Sistemi

Bu dizin, Farmoria oyun motorunun test sistemini içerir. Detaylı dokümantasyon için `docs/testing.md` dosyasına bakabilirsiniz.

## Hızlı Başlangıç

1. Test bağımlılıklarını yükleyin:
```bash
pip install -r requirements.txt
```

2. Testleri çalıştırın:
```bash
pytest
```

## Dizin Yapısı

```
tests/
├── __init__.py
├── conftest.py           # Ortak test fixture'ları
├── test_example.py       # Örnek testler
├── test_core/           # Core modülü testleri
├── test_graphics/       # Grafik modülü testleri
├── test_systems/        # Sistemler modülü testleri
└── test_utils/          # Yardımcı modül testleri
```

## Test Kategorileri

- `test_core/`: Oyun motoru çekirdek bileşenleri testleri
- `test_graphics/`: Grafik sistemi testleri
- `test_systems/`: Alt sistemler (ses, girdi, fizik vb.) testleri
- `test_utils/`: Yardımcı fonksiyonlar ve sınıflar testleri

## Test Yazma Kuralları

1. Her modül için ayrı bir test dosyası oluşturun
2. Test fonksiyonları `test_` ile başlamalıdır
3. Test sınıfları `Test` ile başlamalıdır
4. Her test tek bir işlevi test etmelidir
5. Testler bağımsız olmalıdır

## Örnek Test

```python
import pytest
from engine.core.core import FarmoriaEngine

def test_engine_initialization():
    """Test engine başlatma işlemini kontrol eder."""
    engine = FarmoriaEngine()
    assert engine is not None
    
def test_engine_window_size():
    """Test pencere boyutlarını kontrol eder."""
    engine = FarmoriaEngine(width=800, height=600)
    assert engine.width == 800
    assert engine.height == 600
``` 