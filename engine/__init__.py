"""
Farmoria Game Engine
===================

Modüler yapıda tasarlanmış 2D oyun motoru.

Modüller:
---------
- core: Temel motor işlevleri
- graphics: Grafik işlemleri ve render sistemi
- systems: Oyun sistemleri (fizik, ses, girdi vb.)
- utils: Yardımcı araçlar ve yöneticiler
- components: Oyun nesneleri ve bileşenleri
"""

__version__ = "0.1.0"

from . import core
from . import graphics
from . import systems
from . import utils
from . import components 