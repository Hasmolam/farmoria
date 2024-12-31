# Test Sistemi Dokümantasyonu

## Genel Bakış

Farmoria oyun motoru, kapsamlı bir test sistemi içerir. Bu sistem, pytest framework'ü üzerine kurulmuştur ve aşağıdaki özellikleri sağlar:

- Unit testler
- Test coverage raporlaması
- Fixture'lar
- Parametrize edilmiş testler

## Test Dosyaları

Tüm test dosyaları `tests/` dizini altında bulunur ve aşağıdaki kurallara uyar:

- Test dosya isimleri `test_*.py` formatında olmalıdır
- Test sınıfları `Test*` ile başlamalıdır
- Test fonksiyonları `test_*` ile başlamalıdır

Örnek test dosyası yapısı:

```python
# tests/test_player.py
import pytest
from engine.components.player import Player

def test_player_initialization():
    player = Player(x=100, y=200)
    assert player.x == 100
    assert player.y == 200

@pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
def test_player_movement(direction):
    player = Player()
    if direction == "right":
        player.move(1, 0)
    elif direction == "left":
        player.move(-1, 0)
    elif direction == "down":
        player.move(0, 1)
    else:  # up
        player.move(0, -1)
    assert player.direction == direction
```

## Test Çalıştırma

Testleri çalıştırmak için aşağıdaki komutları kullanabilirsiniz:

```bash
# Tüm testleri çalıştır
pytest

# Belirli bir test dosyasını çalıştır
pytest tests/test_player.py

# Ayrıntılı çıktı ile çalıştır
pytest -v

# Test coverage raporu ile çalıştır
pytest --cov=engine

# HTML coverage raporu oluştur
pytest --cov=engine --cov-report=html
```

## Test Coverage

Test coverage raporları, kodun hangi kısımlarının test edildiğini gösterir. Coverage raporunu görüntülemek için:

1. HTML raporu oluştur: `pytest --cov=engine --cov-report=html`
2. `htmlcov/index.html` dosyasını tarayıcıda aç

## Fixture'lar

Ortak test kurulumları için `conftest.py` dosyasını kullanabilirsiniz:

```python
# tests/conftest.py
import pytest
from engine.core.core import FarmoriaEngine

@pytest.fixture
def game_engine():
    """Test için oyun motoru fixture'ı"""
    engine = FarmoriaEngine()
    yield engine
    engine.quit()

@pytest.fixture
def player():
    """Test için oyuncu fixture'ı"""
    from engine.components.player import Player
    return Player(x=0, y=0)
```

## Test Kategorileri

Testleri kategorize etmek için pytest markers kullanabilirsiniz:

```python
# Yavaş testler için
@pytest.mark.slow
def test_complex_operation():
    pass

# Grafik testleri için
@pytest.mark.graphics
def test_render():
    pass

# Belirli bir kategoriyi çalıştırmak için:
pytest -m graphics
```

## Mock Kullanımı

Bağımlılıkları mock'lamak için `pytest-mock` kullanabilirsiniz:

```python
def test_audio_system(mocker):
    # pygame.mixer.init'i mock'la
    mock_init = mocker.patch('pygame.mixer.init')
    
    from engine.systems.audio import AudioSystem
    audio = AudioSystem()
    
    # Mock'un çağrıldığını doğrula
    mock_init.assert_called_once()
```

## Debug ve Hata Ayıklama

Test çalıştırırken hata ayıklama için:

```bash
# Ayrıntılı çıktı
pytest -v

# Çok ayrıntılı çıktı
pytest -vv

# Debug modunda çalıştır
pytest --pdb

# İlk hatada dur
pytest -x
```

## Test Yazma Önerileri

1. Her test fonksiyonu tek bir şeyi test etmelidir
2. Test isimleri açıklayıcı olmalıdır
3. Testler bağımsız olmalıdır
4. Fixture'ları ortak kurulum için kullanın
5. Edge case'leri test etmeyi unutmayın
6. Test coverage'ı %80'in üzerinde tutmaya çalışın

## Continuous Integration

GitHub Actions ile otomatik test çalıştırma örneği:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=engine --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
``` 