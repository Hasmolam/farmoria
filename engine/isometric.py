import pygame
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
import math
from .texture_atlas import TextureAtlas, TextureRegion

@dataclass
class Tile:
    """İzometrik tile sınıfı"""
    atlas: TextureAtlas
    region_name: str
    tile_type: str
    walkable: bool = True
    elevation: float = 0.0
    properties: Dict = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
    
    @property
    def surface(self) -> pygame.Surface:
        """Tile'ın texture'ını getir"""
        return self.atlas.get_texture(self.region_name)

class IsometricGrid:
    """İzometrik grid sistemi"""
    def __init__(self, tile_width: int, tile_height: int):
        self.tile_width = tile_width  # Tile genişliği (piksel)
        self.tile_height = tile_height  # Tile yüksekliği (piksel)
        self.tiles: Dict[Tuple[int, int], Tile] = {}  # (x, y) -> Tile
        
    def cart_to_iso(self, x: float, y: float) -> Tuple[float, float]:
        """Kartezyen koordinatları izometrik koordinatlara dönüştür"""
        iso_x = (x - y) * (self.tile_width / 2)
        iso_y = (x + y) * (self.tile_height / 2)
        return iso_x, iso_y
    
    def iso_to_cart(self, iso_x: float, iso_y: float) -> Tuple[float, float]:
        """İzometrik koordinatları kartezyen koordinatlara dönüştür"""
        x = (iso_x / self.tile_width + iso_y / self.tile_height) / 2
        y = (iso_y / self.tile_height - iso_x / self.tile_width) / 2
        return x, y
    
    def get_tile_position(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Grid koordinatlarını ekran koordinatlarına dönüştür"""
        return self.cart_to_iso(grid_x, grid_y)
    
    def get_grid_position(self, screen_x: float, screen_y: float) -> Tuple[int, int]:
        """Ekran koordinatlarını en yakın grid koordinatlarına dönüştür"""
        cart_x, cart_y = self.iso_to_cart(screen_x, screen_y)
        return round(cart_x), round(cart_y)

class TileMap:
    """İzometrik tile harita sistemi"""
    def __init__(self, grid: IsometricGrid):
        self.grid = grid
        self.layers: Dict[int, Dict[Tuple[int, int], Tile]] = {0: {}}
        self.current_layer = 0
    
    def add_layer(self, layer_id: int):
        """Yeni bir katman ekle"""
        if layer_id not in self.layers:
            self.layers[layer_id] = {}
    
    def set_tile(self, x: int, y: int, tile: Tile, layer: int = None):
        """Belirtilen konuma tile yerleştir"""
        if layer is None:
            layer = self.current_layer
        if layer not in self.layers:
            self.add_layer(layer)
        self.layers[layer][(x, y)] = tile
    
    def get_tile(self, x: int, y: int, layer: int = None) -> Optional[Tile]:
        """Belirtilen konumdaki tile'ı getir"""
        if layer is None:
            layer = self.current_layer
        return self.layers.get(layer, {}).get((x, y))
    
    def remove_tile(self, x: int, y: int, layer: int = None):
        """Belirtilen konumdaki tile'ı kaldır"""
        if layer is None:
            layer = self.current_layer
        if layer in self.layers and (x, y) in self.layers[layer]:
            del self.layers[layer][(x, y)]
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Belirtilen konumun yürünebilir olup olmadığını kontrol et"""
        for layer in sorted(self.layers.keys()):
            tile = self.get_tile(x, y, layer)
            if tile and not tile.walkable:
                return False
        return True
    
    def get_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A* algoritması ile iki nokta arasındaki yolu bul"""
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
        
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = pos
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)
            ]
            return [n for n in neighbors if self.is_walkable(*n)]
        
        # A* algoritması implementasyonu
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = frontier.pop(0)[1]
            
            if current == end:
                break
                
            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(end, next_pos)
                    frontier.append((priority, next_pos))
                    frontier.sort()
                    came_from[next_pos] = current
        
        # Yolu oluştur
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        
        return path if path[0] == start else []

class IsometricRenderer:
    """İzometrik render sistemi"""
    def __init__(self, tilemap: TileMap):
        self.tilemap = tilemap
        # Çift tamponlama için arka tampon oluştur
        self.back_buffer = None
        # Shader sistemi
        self.shader_system = None
        self.current_shader = None
        self.light_positions = []
        
    def init_shader_system(self, width: int, height: int):
        """Shader sistemini başlat"""
        from .shader_system import ShaderSystem
        self.shader_system = ShaderSystem(width, height)
        
    def resize(self, width: int, height: int):
        """Render hedefinin boyutunu değiştir"""
        self.back_buffer = pygame.Surface((width, height), pygame.SRCALPHA)
        if self.shader_system is None:
            self.init_shader_system(width, height)
        
    def add_light(self, x: float, y: float, radius: float = 1.0, color: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """Işık kaynağı ekle"""
        self.light_positions.append({
            'position': (x, y),
            'radius': radius,
            'color': color
        })
        
    def clear_lights(self):
        """Tüm ışık kaynaklarını temizle"""
        self.light_positions.clear()
        
    def use_shader(self, shader_name: str):
        """Shader seç"""
        if self.shader_system:
            self.current_shader = shader_name
            self.shader_system.use_shader(shader_name)
        
    def set_shader_param(self, name: str, value: any):
        """Shader parametresi ayarla"""
        if self.shader_system:
            self.shader_system.set_uniform(name, value)
        
    def is_tile_visible(self, screen_x: float, screen_y: float, tile_width: float, tile_height: float, 
                       screen_width: float, screen_height: float) -> bool:
        """Tile'ın ekranda görünür olup olmadığını kontrol et"""
        # Tile'ın köşe noktalarını hesapla
        left = screen_x
        right = screen_x + tile_width
        top = screen_y
        bottom = screen_y + tile_height
        
        # Ekran sınırlarını genişlet (tile'ın bir kısmı görünüyorsa da çiz)
        buffer = max(tile_width, tile_height)
        screen_left = -buffer
        screen_right = screen_width + buffer
        screen_top = -buffer
        screen_bottom = screen_height + buffer
        
        # Tile'ın tamamen ekran dışında olup olmadığını kontrol et
        if (right < screen_left or
            left > screen_right or
            bottom < screen_top or
            top > screen_bottom):
            return False
        return True
        
    def get_visible_range(self, screen_width: float, screen_height: float, 
                         camera_x: float, camera_y: float) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Ekranda görünür olabilecek grid koordinat aralığını hesapla"""
        # Ekran köşelerinin dünya koordinatlarını hesapla
        top_left = self.tilemap.grid.iso_to_cart(
            camera_x,
            camera_y
        )
        bottom_right = self.tilemap.grid.iso_to_cart(
            camera_x + screen_width,
            camera_y + screen_height
        )
        
        # Görünür aralığı genişlet (kenar tile'ları için)
        buffer = 2
        min_x = int(min(top_left[0], bottom_right[0])) - buffer
        min_y = int(min(top_left[1], bottom_right[1])) - buffer
        max_x = int(max(top_left[0], bottom_right[0])) + buffer
        max_y = int(max(top_left[1], bottom_right[1])) + buffer
        
        return (min_x, min_y), (max_x, max_y)
        
    def render(self, target_surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Tile haritasını render et"""
        # Arka tampon boyutunu kontrol et ve gerekirse güncelle
        screen_width = target_surface.get_width()
        screen_height = target_surface.get_height()
        if (self.back_buffer is None or 
            self.back_buffer.get_width() != screen_width or 
            self.back_buffer.get_height() != screen_height):
            self.resize(screen_width, screen_height)
        
        # Arka tamponu temizle
        self.back_buffer.fill((0, 0, 0, 0))
        
        # Görünür grid aralığını hesapla
        (min_x, min_y), (max_x, max_y) = self.get_visible_range(
            screen_width, screen_height, camera_x, camera_y
        )
        
        # Görünür tile'ları topla
        visible_tiles = []
        for layer in sorted(self.tilemap.layers.keys()):
            for (grid_x, grid_y), tile in self.tilemap.layers[layer].items():
                if not tile:
                    continue
                    
                # Grid koordinatları görünür aralıkta mı kontrol et
                if not (min_x <= grid_x <= max_x and min_y <= grid_y <= max_y):
                    continue
                    
                # Tile'ın ekran pozisyonunu hesapla
                iso_x, iso_y = self.tilemap.grid.get_tile_position(grid_x, grid_y)
                screen_x = iso_x - camera_x
                screen_y = iso_y - camera_y - (tile.elevation * self.tilemap.grid.tile_height)
                
                # Tile ekranda görünür mü kontrol et
                if not self.is_tile_visible(screen_x, screen_y, 
                                         self.tilemap.grid.tile_width,
                                         self.tilemap.grid.tile_height,
                                         screen_width, screen_height):
                    continue
                
                # Görünür tile'ı listeye ekle (derinlik sıralaması için)
                visible_tiles.append((layer, grid_x + grid_y, tile, screen_x, screen_y))
        
        # Tile'ları derinliğe göre sırala ve arka tampona çiz
        for layer, depth, tile, screen_x, screen_y in sorted(visible_tiles, key=lambda x: (x[0], x[1])):
            self.back_buffer.blit(tile.surface, (screen_x, screen_y))
        
        # Shader efektlerini uygula
        if self.shader_system and self.current_shader:
            # Işıklandırma shader'ı için parametreleri ayarla
            if self.current_shader == 'lighting':
                for light in self.light_positions:
                    self.set_shader_param('light_position', light['position'])
                    self.set_shader_param('light_radius', light['radius'])
                    self.set_shader_param('light_color', light['color'])
                    self.set_shader_param('ambient_strength', 0.2)
            
            # Blur shader'ı için parametreleri ayarla
            elif self.current_shader == 'blur':
                self.set_shader_param('resolution', (screen_width, screen_height))
                self.set_shader_param('blur_radius', 3.0)
            
            # Shader'ı uygula
            self.back_buffer = self.shader_system.render_to_texture(self.back_buffer)
        
        # Arka tamponu ana yüzeye kopyala
        target_surface.blit(self.back_buffer, (0, 0)) 