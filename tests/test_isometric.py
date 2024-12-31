import pytest
import pygame
from engine.isometric import IsometricGrid, TileMap, Tile, IsometricRenderer
from engine.texture_atlas import TextureAtlas, TextureRegion

@pytest.fixture
def grid():
    return IsometricGrid(64, 32)  # 64x32 piksel tile boyutu

@pytest.fixture
def atlas():
    atlas = TextureAtlas((256, 256))
    surface = pygame.Surface((64, 32))
    surface.fill((255, 0, 0))  # Kırmızı test tile'ı
    atlas.add_texture("grass", surface)
    surface = pygame.Surface((64, 32))
    surface.fill((0, 0, 255))  # Mavi test tile'ı
    atlas.add_texture("wall", surface)
    return atlas

@pytest.fixture
def basic_tile(atlas):
    return Tile(
        atlas=atlas,
        region_name="grass",
        tile_type="grass",
        walkable=True,
        elevation=0.0
    )

@pytest.fixture
def tilemap(grid):
    return TileMap(grid)

@pytest.fixture
def renderer(tilemap):
    return IsometricRenderer(tilemap)

def test_grid_initialization(grid):
    """Grid sisteminin doğru başlatıldığını kontrol et"""
    assert grid.tile_width == 64
    assert grid.tile_height == 32
    assert isinstance(grid.tiles, dict)

def test_coordinate_conversion(grid):
    """Koordinat dönüşümlerinin doğruluğunu test et"""
    # Kartezyen -> İzometrik
    iso_x, iso_y = grid.cart_to_iso(1, 1)
    assert iso_x == 0  # (1 - 1) * 32 = 0
    assert iso_y == 32  # (1 + 1) * 16 = 32
    
    # İzometrik -> Kartezyen (yaklaşık değerler)
    cart_x, cart_y = grid.iso_to_cart(0, 32)
    assert pytest.approx(cart_x, rel=0.1) == 0.5
    assert pytest.approx(cart_y, rel=0.1) == 0.5

def test_tile_creation(basic_tile):
    """Tile özelliklerinin doğru ayarlandığını kontrol et"""
    assert basic_tile.tile_type == "grass"
    assert basic_tile.walkable == True
    assert basic_tile.elevation == 0.0
    assert isinstance(basic_tile.properties, dict)
    assert basic_tile.surface is not None
    assert isinstance(basic_tile.surface, pygame.Surface)

def test_tilemap_operations(tilemap, basic_tile):
    """TileMap operasyonlarını test et"""
    # Tile ekleme
    tilemap.set_tile(0, 0, basic_tile)
    assert tilemap.get_tile(0, 0) == basic_tile
    
    # Katman ekleme
    tilemap.add_layer(1)
    assert 1 in tilemap.layers
    
    # Farklı katmana tile ekleme
    tilemap.set_tile(0, 0, basic_tile, layer=1)
    assert tilemap.get_tile(0, 0, layer=1) == basic_tile
    
    # Tile silme
    tilemap.remove_tile(0, 0)
    assert tilemap.get_tile(0, 0) is None

def test_walkability(tilemap, atlas, basic_tile):
    """Yürünebilirlik kontrolünü test et"""
    # Yürünebilir tile
    tilemap.set_tile(0, 0, basic_tile)
    assert tilemap.is_walkable(0, 0) == True
    
    # Yürünemez tile
    unwalkable_tile = Tile(
        atlas=atlas,
        region_name="wall",
        tile_type="wall",
        walkable=False
    )
    tilemap.set_tile(1, 1, unwalkable_tile)
    assert tilemap.is_walkable(1, 1) == False

def test_pathfinding(tilemap, atlas, basic_tile):
    """A* yol bulma algoritmasını test et"""
    # 3x3'lük test haritası oluştur
    for x in range(3):
        for y in range(3):
            tilemap.set_tile(x, y, basic_tile)
    
    # Ortadaki tile'ı yürünemez yap
    wall_tile = Tile(
        atlas=atlas,
        region_name="wall",
        tile_type="wall",
        walkable=False
    )
    tilemap.set_tile(1, 1, wall_tile)
    
    # Yol bulma
    path = tilemap.get_path((0, 0), (2, 2))
    assert len(path) > 0
    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)
    assert (1, 1) not in path  # Duvarın etrafından dolaşmalı

def test_tile_visibility(renderer):
    """Tile görünürlük kontrolünü test et"""
    # Ekran içindeki tile
    assert renderer.is_tile_visible(
        screen_x=100,
        screen_y=100,
        tile_width=64,
        tile_height=32,
        screen_width=800,
        screen_height=600
    ) == True
    
    # Ekran dışındaki tile (tamamen sol dışında)
    assert renderer.is_tile_visible(
        screen_x=-200,
        screen_y=100,
        tile_width=64,
        tile_height=32,
        screen_width=800,
        screen_height=600
    ) == False
    
    # Ekran dışındaki tile (tamamen sağ dışında)
    assert renderer.is_tile_visible(
        screen_x=1000,
        screen_y=100,
        tile_width=64,
        tile_height=32,
        screen_width=800,
        screen_height=600
    ) == False
    
    # Ekran dışındaki tile (tamamen üst dışında)
    assert renderer.is_tile_visible(
        screen_x=100,
        screen_y=-200,
        tile_width=64,
        tile_height=32,
        screen_width=800,
        screen_height=600
    ) == False
    
    # Ekran dışındaki tile (tamamen alt dışında)
    assert renderer.is_tile_visible(
        screen_x=100,
        screen_y=800,
        tile_width=64,
        tile_height=32,
        screen_width=800,
        screen_height=600
    ) == False
    
    # Kısmen görünür tile (sol kenar)
    assert renderer.is_tile_visible(
        screen_x=-32,
        screen_y=100,
        tile_width=64,
        tile_height=32,
        screen_width=800,
        screen_height=600
    ) == True

def test_visible_range(renderer):
    """Görünür grid aralığı hesaplamasını test et"""
    # Test parametreleri
    screen_width = 800
    screen_height = 600
    camera_x = 0
    camera_y = 0
    
    # Görünür aralığı hesapla
    (min_x, min_y), (max_x, max_y) = renderer.get_visible_range(
        screen_width, screen_height, camera_x, camera_y
    )
    
    # Aralık değerlerinin mantıklı olduğunu kontrol et
    assert min_x < max_x
    assert min_y < max_y
    assert isinstance(min_x, int)
    assert isinstance(min_y, int)
    assert isinstance(max_x, int)
    assert isinstance(max_y, int)

def test_culling_render(renderer, tilemap, basic_tile):
    """View culling ile render işlemini test et"""
    surface = pygame.Surface((800, 600))
    
    # Görünür tile'lar
    tilemap.set_tile(0, 0, basic_tile)
    tilemap.set_tile(1, 1, basic_tile)
    
    # Ekran dışı tile'lar (çok uzakta)
    tilemap.set_tile(100, 100, basic_tile)
    tilemap.set_tile(-100, -100, basic_tile)
    
    # Render işlemi
    renderer.render(surface)
    
    # Farklı kamera pozisyonları ile test
    renderer.render(surface, camera_x=100, camera_y=100)
    renderer.render(surface, camera_x=-100, camera_y=-100)

def test_texture_atlas(atlas):
    """Texture atlas sistemini test et"""
    # Atlas boyutları
    assert atlas.texture_size == (256, 256)
    
    # Texture bölgeleri
    grass_region = atlas.get_region("grass")
    assert grass_region is not None
    assert grass_region.width == 64
    assert grass_region.height == 32
    
    wall_region = atlas.get_region("wall")
    assert wall_region is not None
    assert wall_region.width == 64
    assert wall_region.height == 32
    
    # Texture'ları getirme
    grass_texture = atlas.get_texture("grass")
    assert grass_texture is not None
    assert isinstance(grass_texture, pygame.Surface)
    assert grass_texture.get_size() == (64, 32)
    
    wall_texture = atlas.get_texture("wall")
    assert wall_texture is not None
    assert isinstance(wall_texture, pygame.Surface)
    assert wall_texture.get_size() == (64, 32)

def test_double_buffering(renderer):
    """Çift tamponlama sistemini test et"""
    # İlk render için yüzey oluştur
    surface = pygame.Surface((800, 600))
    
    # İlk render - arka tampon oluşturulmalı
    renderer.render(surface)
    assert renderer.back_buffer is not None
    assert renderer.back_buffer.get_size() == (800, 600)
    
    # Farklı boyutta render - arka tampon yeniden oluşturulmalı
    new_surface = pygame.Surface((1024, 768))
    renderer.render(new_surface)
    assert renderer.back_buffer.get_size() == (1024, 768)
    
    # Aynı boyutta render - mevcut arka tampon kullanılmalı
    old_back_buffer = renderer.back_buffer
    renderer.render(new_surface)
    assert renderer.back_buffer is old_back_buffer 

def test_shader_system(renderer):
    """Shader sistemini test et"""
    # Shader sistemini başlat
    renderer.init_shader_system(800, 600)
    assert renderer.shader_system is not None
    
    # Shader seçimi
    renderer.use_shader('lighting')
    assert renderer.current_shader == 'lighting'
    
    # Işık kaynağı ekleme
    renderer.add_light(100, 100, 2.0, (1.0, 0.8, 0.6))
    assert len(renderer.light_positions) == 1
    light = renderer.light_positions[0]
    assert light['position'] == (100, 100)
    assert light['radius'] == 2.0
    assert light['color'] == (1.0, 0.8, 0.6)
    
    # Işık kaynaklarını temizleme
    renderer.clear_lights()
    assert len(renderer.light_positions) == 0
    
    # Blur shader'ına geçiş
    renderer.use_shader('blur')
    assert renderer.current_shader == 'blur'
    
    # Shader parametresi ayarlama
    renderer.set_shader_param('blur_radius', 5.0)

def test_shader_render(renderer, tilemap, basic_tile):
    """Shader ile render işlemini test et"""
    # Test yüzeyi oluştur
    surface = pygame.Surface((800, 600))
    
    # Shader sistemini başlat
    renderer.init_shader_system(800, 600)
    
    # Test tile'ları ekle
    tilemap.set_tile(0, 0, basic_tile)
    tilemap.set_tile(1, 1, basic_tile)
    
    # Işıklandırma shader'ı ile render
    renderer.use_shader('lighting')
    renderer.add_light(400, 300, 3.0)
    renderer.render(surface)
    
    # Blur shader'ı ile render
    renderer.use_shader('blur')
    renderer.render(surface)
    
    # Shader'sız render
    renderer.use_shader(None)
    renderer.render(surface) 