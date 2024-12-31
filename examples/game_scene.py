from engine.scene import Scene, SceneState
from engine.physics import PhysicsWorld, CollisionType
from engine.ui import Button, Label, Panel, Alignment
import pygame
import random
import math

class GameScene(Scene):
    def __init__(self):
        super().__init__()
        self.physics = None
        self.ui_panel = None
        self.pause_panel = None
        self.inventory_panel = None
        self.score = 0
        self.health = 100
        self.player = None
        self.platforms = []
        self.collectibles = []
        self.enemies = []
        self._setup_complete = False
    
    async def preload(self):
        """Assetleri ve kaynakları önceden yükle"""
        try:
            print("Scene yükleniyor...")
            await super().preload()
            
            # Fizik dünyasını oluştur
            self.physics = PhysicsWorld()
            self.physics.set_gravity((0, 981))
            
            # UI panelini oluştur
            self.ui_panel = Panel(10, 10, 200, 100, bg_color=(30, 30, 30, 150))
            
            # Skor ve sağlık göstergeleri
            self.score_label = Label(20, 20, "Skor: 0", color=(255, 255, 255))
            self.health_bar = Panel(20, 50, 160, 20, bg_color=(200, 0, 0))
            self.health_fill = Panel(20, 50, 160, 20, bg_color=(0, 200, 0))
            
            self.ui_panel.add_child(self.score_label)
            self.ui_panel.add_child(self.health_bar)
            self.ui_panel.add_child(self.health_fill)
            
            # Pause menüsü
            screen = pygame.display.get_surface()
            self.pause_panel = Panel(
                screen.get_width()//2 - 150,
                screen.get_height()//2 - 200,
                300, 400,
                bg_color=(30, 30, 30, 200)
            )
            
            resume_btn = Button(50, 100, 200, 50, "Devam Et", 
                              bg_color=(34, 139, 34),
                              callback=self._toggle_pause)
            
            quit_btn = Button(50, 200, 200, 50, "Menüye Dön",
                            bg_color=(139, 34, 34),
                            callback=self._quit_to_menu)
            
            self.pause_panel.add_child(resume_btn)
            self.pause_panel.add_child(quit_btn)
            
            # Envanter paneli
            self.inventory_panel = Panel(
                screen.get_width() - 210, 10,
                200, 300,
                bg_color=(30, 30, 30, 150)
            )
            
            inv_title = Label(100, 30, "Envanter", color=(255, 255, 255),
                            alignment=Alignment.CENTER)
            self.inventory_panel.add_child(inv_title)
            
            self._create_game_objects()
            self._setup_complete = True
            
        except Exception as e:
            print(f"Hata: {str(e)}")
            raise
    
    def _create_game_objects(self):
        """Oyun nesnelerini oluştur"""
        if not self.physics:
            return
            
        # Oyuncu karakteri
        player_body, player_shape = self.physics.create_box(
            pos=(400, 300),
            size=(30, 50),
            mass=1.0
        )
        self.physics.apply_material(player_shape, 'metal')
        player_shape.collision_type = CollisionType.PLAYER
        self.player = (player_body, player_shape)
        
        # Platformlar - farklı materyaller
        materials = ['wood', 'ice', 'metal']
        for i in range(5):
            x = 200 + i * 150
            material = materials[i % len(materials)]
            platform_body, platform_shape = self.physics.create_box(
                pos=(x, 500),
                size=(100, 20),
                mass=0
            )
            self.physics.apply_material(platform_shape, material)
            platform_shape.collision_type = CollisionType.PLATFORM
            self.platforms.append((platform_body, platform_shape, material))
        
        # Toplanabilir nesneler
        for _ in range(10):
            x = random.randint(100, 700)
            y = random.randint(100, 400)
            collect_body, collect_shape = self.physics.create_box(
                pos=(x, y),
                size=(20, 20),
                mass=0.1
            )
            collect_shape.collision_type = CollisionType.ITEM
            self.collectibles.append((collect_body, collect_shape))
        
        # Düşman nesneler
        for _ in range(3):
            x = random.randint(100, 700)
            y = random.randint(100, 300)
            enemy_body, enemy_shape = self.physics.create_box(
                pos=(x, y),
                size=(40, 40),
                mass=2.0
            )
            self.physics.apply_material(enemy_shape, 'metal')
            enemy_shape.collision_type = CollisionType.ENEMY
            self.enemies.append((enemy_body, enemy_shape))
        
        # Çarpışma callbackleri
        def player_item_collision(player_shape, item_shape):
            self.score += 10
            self.score_label.text = f"Skor: {self.score}"
            # Toplanabilir nesneyi kaldır
            for body, shape in self.collectibles[:]:
                if shape == item_shape:
                    self.collectibles.remove((body, shape))
                    self.physics.space.remove(body, shape)
        
        def player_enemy_collision(player_shape, enemy_shape):
            self.health = max(0, self.health - 10)
            self._update_health_bar()
        
        self.physics.add_collision_callback(
            CollisionType.PLAYER,
            CollisionType.ITEM,
            player_item_collision
        )
        
        self.physics.add_collision_callback(
            CollisionType.PLAYER,
            CollisionType.ENEMY,
            player_enemy_collision
        )
    
    def _update_health_bar(self):
        """Sağlık barını güncelle"""
        health_width = (self.health / 100) * 160
        self.health_fill.width = health_width
    
    def _toggle_pause(self):
        """Oyunu duraklat/devam ettir"""
        if self.state == SceneState.PAUSED:
            self.resume()
        else:
            self.pause()
    
    def _quit_to_menu(self):
        """Ana menüye dön"""
        self.engine.scene_manager.set_scene("menu")
    
    def _update_scene(self, dt: float):
        """Scene mantığını güncelle"""
        if not self._setup_complete or self.state == SceneState.PAUSED:
            return
        
        # Fizik motorunu güncelle
        if self.physics:
            self.physics.update(dt)
        
        # Oyuncu kontrollerini işle
        if self.player:
            player_body = self.player[0]
            keys = pygame.key.get_pressed()
            
            # Yatay hareket
            if keys[pygame.K_LEFT]:
                player_body.apply_impulse_at_local_point((-1000 * dt, 0), (0, 0))
            if keys[pygame.K_RIGHT]:
                player_body.apply_impulse_at_local_point((1000 * dt, 0), (0, 0))
            
            # Zıplama
            if keys[pygame.K_SPACE]:
                player_body.apply_impulse_at_local_point((0, -2000 * dt), (0, 0))
            
            # Dash hareketi
            if keys[pygame.K_LSHIFT]:
                vel_x = 2000 if keys[pygame.K_RIGHT] else -2000 if keys[pygame.K_LEFT] else 0
                player_body.velocity = (vel_x, player_body.velocity.y)
        
        # Düşmanları hareket ettir
        for enemy_body, _ in self.enemies:
            # Basit AI: Oyuncuya doğru hareket et
            if self.player:
                player_pos = self.player[0].position
                enemy_pos = enemy_body.position
                
                # Yön vektörü
                dx = player_pos.x - enemy_pos.x
                dy = player_pos.y - enemy_pos.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    # Normalize ve hızı uygula
                    dx, dy = dx/dist * 500, dy/dist * 500
                    enemy_body.velocity = (dx, dy)
    
    def _draw_scene(self, screen: pygame.Surface):
        """Scene'i çiz"""
        if not self._setup_complete:
            return
        
        # Arka planı temizle
        screen.fill((20, 20, 40))
        
        # Platform renklerini ayarla
        material_colors = {
            'wood': (139, 69, 19),    # Kahverengi
            'ice': (200, 200, 255),   # Açık mavi
            'metal': (169, 169, 169)  # Gri
        }
        
        # Platformları çiz
        for _, shape, material in self.platforms:
            points = shape.get_vertices()
            color = material_colors.get(material, (200, 200, 200))
            pygame.draw.polygon(screen, color, points)
        
        # Toplanabilir nesneleri çiz
        for _, shape in self.collectibles:
            points = shape.get_vertices()
            pygame.draw.polygon(screen, (255, 215, 0), points)  # Altın rengi
        
        # Düşmanları çiz
        for _, shape in self.enemies:
            points = shape.get_vertices()
            pygame.draw.polygon(screen, (255, 0, 0), points)  # Kırmızı
        
        # Oyuncuyu çiz
        if self.player:
            points = self.player[1].get_vertices()
            pygame.draw.polygon(screen, (0, 255, 0), points)  # Yeşil
        
        # UI'ı çiz
        if self.ui_panel:
            self.ui_panel.draw(screen)
        
        if self.inventory_panel:
            self.inventory_panel.draw(screen)
        
        # Pause menüsünü çiz
        if self.state == SceneState.PAUSED and self.pause_panel:
            self.pause_panel.draw(screen)
    
    def _handle_scene_event(self, event: pygame.event.Event):
        """Olay işleme"""
        if not self._setup_complete:
            return
        
        # UI olaylarını işle
        if self.ui_panel:
            self.ui_panel.handle_event(event)
        
        if self.inventory_panel:
            self.inventory_panel.handle_event(event)
        
        if self.state == SceneState.PAUSED and self.pause_panel:
            self.pause_panel.handle_event(event)
        
        # ESC tuşu ile pause menüsü
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._toggle_pause()
        
        # Tab tuşu ile envanter
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.inventory_panel.visible = not self.inventory_panel.visible 