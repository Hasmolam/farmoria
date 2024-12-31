import pytest
import pygame
from engine.systems.isometric import IsometricGrid, TileMap, Tile, IsometricRenderer
from engine.graphics.texture_atlas import TextureAtlas

@pytest.fixture
def isometric_grid():
    """IsometricGrid fixture'ı"""
    return IsometricGrid(tile_width=64, tile_height=32)

@pytest.fixture
def tile_map():
    """TileMap fixture'ı"""
    grid = IsometricGrid(tile_width=64, tile_height=32)
    return TileMap(grid, width=10, height=10)

@pytest.fixture
def test_tile(tile_map):
    """Test için Tile fixture'ı"""
    atlas = TextureAtlas()
    return Tile(atlas=atlas, region_name="test", tile_type="grass")

@pytest.fixture
def renderer():
    """IsometricRenderer fixture'ı"""
    screen = pygame.Surface((800, 600))
    grid = IsometricGrid(tile_width=64, tile_height=32)
    return IsometricRenderer(screen, grid)

class TestIsometricGrid:
    """IsometricGrid test sınıfı"""
    
    def test_grid_initialization(self, isometric_grid):
        """Grid başlatma testi"""
        assert isometric_grid.tile_width == 64
        assert isometric_grid.tile_height == 32
        
    def test_cart_to_iso(self, isometric_grid):
        """Kartezyen koordinatları izometrik koordinatlara çevirme testi"""
        cart_x, cart_y = 100, 100
        iso_x, iso_y = isometric_grid.cart_to_iso(cart_x, cart_y)
        assert isinstance(iso_x, (int, float))
        assert isinstance(iso_y, (int, float))
        
    def test_iso_to_cart(self, isometric_grid):
        """İzometrik koordinatları kartezyen koordinatlara çevirme testi"""
        iso_x, iso_y = 100, 100
        cart_x, cart_y = isometric_grid.iso_to_cart(iso_x, iso_y)
        assert isinstance(cart_x, (int, float))
        assert isinstance(cart_y, (int, float))
        
class TestTileMap:
    """TileMap test sınıfı"""
    
    def test_map_initialization(self, tile_map):
        """Harita başlatma testi"""
        assert tile_map.width == 10
        assert tile_map.height == 10
        assert len(tile_map.tiles) == 10
        assert all(len(row) == 10 for row in tile_map.tiles)
        assert all(tile is None for row in tile_map.tiles for tile in row)
        
    def test_get_tile(self, tile_map):
        """Tile alma testi"""
        tile = tile_map.get_tile(5, 5)
        assert tile is None  # Başlangıçta None olmalı
        
    def test_set_tile(self, tile_map, test_tile):
        """Tile ayarlama testi"""
        tile_map.set_tile(5, 5, test_tile)
        assert tile_map.get_tile(5, 5) == test_tile
        
    def test_is_valid_position(self, tile_map):
        """Geçerli pozisyon kontrolü testi"""
        assert tile_map.is_valid_position(0, 0)
        assert tile_map.is_valid_position(9, 9)
        assert not tile_map.is_valid_position(-1, 0)
        assert not tile_map.is_valid_position(10, 10)
        
class TestIsometricRenderer:
    """IsometricRenderer test sınıfı"""
    
    def test_renderer_initialization(self, renderer):
        """Renderer başlatma testi"""
        assert isinstance(renderer.screen, pygame.Surface)
        assert isinstance(renderer.grid, IsometricGrid)
        
    def test_world_to_screen(self, renderer):
        """Dünya koordinatlarını ekran koordinatlarına çevirme testi"""
        world_x, world_y = 5, 5
        screen_x, screen_y = renderer.world_to_screen(world_x, world_y)
        assert isinstance(screen_x, (int, float))
        assert isinstance(screen_y, (int, float))
        
    def test_screen_to_world(self, renderer):
        """Ekran koordinatlarını dünya koordinatlarına çevirme testi"""
        screen_x, screen_y = 400, 300
        world_x, world_y = renderer.screen_to_world(screen_x, screen_y)
        assert isinstance(world_x, (int, float))
        assert isinstance(world_y, (int, float)) 