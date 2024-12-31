from engine.scene import Scene
from engine.ui import Button, Label, Panel, Alignment
import pygame

class MenuScene(Scene):
    def __init__(self):
        super().__init__()
        self.main_panel = None
        self.buttons = {}
    
    async def preload(self):
        """UI elemanlarını yükle"""
        await super().preload()
        
        screen = pygame.display.get_surface()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Gri panel - ekranın sağ tarafında
        panel_width = 300
        panel_height = screen_height
        panel_x = screen_width - panel_width
        panel_y = 0
        
        self.main_panel = Panel(
            panel_x, panel_y, panel_width, panel_height,
            bg_color=(30, 30, 30, 200),
            border_color=None  # Kenarlık yok
        )
        
        # Başlık - panelin üst kısmında ortala
        title = Label(
            panel_width // 2, 100, "Farmoria",
            color=(255, 255, 255),
            font_size=48,
            alignment=Alignment.CENTER
        )
        self.main_panel.children.append(title)
        
        # Düğmeler - dikey olarak eşit aralıklarla yerleştir
        button_configs = [
            ("play", "Oyna"),
            ("settings", "Ayarlar"),
            ("quit", "Çıkış")
        ]
        
        button_width = 200
        button_height = 50
        button_spacing = 30  # Düğmeler arası boşluk
        
        # Butonların toplam yüksekliği
        total_buttons_height = len(button_configs) * (button_height + button_spacing) - button_spacing
        
        # Butonları panelin ortasından başlat
        start_y = (panel_height - total_buttons_height) // 2
        
        for i, (btn_id, text) in enumerate(button_configs):
            button_y = start_y + i * (button_height + button_spacing)
            button = Button(
                (panel_width - button_width) // 2,  # Yatayda ortala
                button_y,
                button_width, button_height,
                text=text,
                text_color=(255, 255, 255),
                bg_color=(34, 139, 34),  # Forest Green
                hover_color=(50, 205, 50)  # Lime Green
            )
            
            if btn_id == "play":
                button.callback = self._on_play_click
            elif btn_id == "settings":
                button.callback = self._on_settings_click
            elif btn_id == "quit":
                button.callback = self._on_quit_click
                
            self.buttons[btn_id] = button
            self.main_panel.children.append(button)
        
        self.loading_progress = 1.0
    
    def _on_play_click(self):
        """Oyna düğmesi tıklama olayı"""
        print("Oyun başlatılıyor...")  # Debug için
        self.engine.scene_manager.set_scene("game", {"level": 1})
    
    def _on_settings_click(self):
        """Ayarlar düğmesi tıklama olayı"""
        print("Ayarlar henüz mevcut değil")  # Debug için
        pass
    
    def _on_quit_click(self):
        """Çıkış düğmesi tıklama olayı"""
        print("Oyundan çıkılıyor...")  # Debug için
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def _draw_scene(self, screen: pygame.Surface):
        """Menüyü çiz"""
        # Arka plan - koyu mavi gradient
        screen.fill((20, 20, 40))
        
        # UI elemanlarını çiz
        if self.main_panel:
            self.main_panel.draw(screen)
    
    def _handle_scene_event(self, event: pygame.event.Event):
        """Olay işleme"""
        # UI olaylarını işle
        if self.main_panel:
            self.main_panel.handle_event(event) 