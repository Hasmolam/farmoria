import pygame
import sys
import math
import os
from engine.animation import Skeleton, Animation

# Pygame başlat
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("İskelet Animasyon Demo")

# FPS ayarları
clock = pygame.time.Clock()
FPS = 60

# Sprite sheet'i yükle
sprite_sheet = pygame.image.load(os.path.join("assets", "character_sheet.png")).convert_alpha()

# Sprite bölgelerini tanımla
sprite_regions = {
    "body": (0, 0, 32, 48),      # Gövde
    "head": (40, 0, 24, 24),     # Kafa
    "right_arm": (80, 0, 16, 32), # Sağ kol
    "left_arm": (120, 0, 16, 32), # Sol kol
    "right_leg": (160, 0, 16, 32),# Sağ bacak
    "left_leg": (200, 0, 16, 32)  # Sol bacak
}

# İskelet oluştur
skeleton = Skeleton()
skeleton.load_sprite_sheet(sprite_sheet, sprite_regions)

# Ana kemikleri ekle
skeleton.add_bone("body", length=48, angle=-math.pi/2)  # Ana gövde dikey olsun
skeleton.add_bone("head", length=24, parent_name="body", position=(0, 0))  # Kafa gövdenin üstünde

# Kolları ekle - gövdenin üst kısmına bağlı
skeleton.add_bone("right_arm", length=32, parent_name="body", position=(8, -8), angle=math.pi/2)  # Sağ kol
skeleton.add_bone("left_arm", length=32, parent_name="body", position=(-8, -8), angle=math.pi/2)  # Sol kol

# Bacakları ekle - gövdenin alt kısmına bağlı
skeleton.add_bone("right_leg", length=32, parent_name="body", position=(8, 40), angle=math.pi/2)  # Sağ bacak
skeleton.add_bone("left_leg", length=32, parent_name="body", position=(-8, 40), angle=math.pi/2)  # Sol bacak

# Sprite'ları kemiklere bağla - offset'leri düzelt
skeleton.set_bone_sprite("body", "body", (-16, -24))  # Gövde merkezi
skeleton.set_bone_sprite("head", "head", (-12, -12))  # Kafa merkezi
skeleton.set_bone_sprite("right_arm", "right_arm", (-8, -16))  # Sağ kol merkezi
skeleton.set_bone_sprite("left_arm", "left_arm", (-8, -16))  # Sol kol merkezi
skeleton.set_bone_sprite("right_leg", "right_leg", (-8, -16))  # Sağ bacak merkezi
skeleton.set_bone_sprite("left_leg", "left_leg", (-8, -16))  # Sol bacak merkezi

# Sol taraf sprite'larını çevir
skeleton.bones["left_arm"].flip_x = True
skeleton.bones["left_leg"].flip_x = True

# Basit yürüme animasyonu oluştur
walk = Animation("walk", duration=0.6)  # Animasyonu biraz yavaşlat

# Başlangıç pozu
walk.add_keyframe(0.0, {
    "body": (0, 0, -math.pi/2),  # Gövde dikey
    "head": (0, 0, 0),  # Kafa düz
    "right_arm": (8, -8, math.pi/2 - math.pi/6),  # Sağ kol hafif arkada
    "left_arm": (-8, -8, math.pi/2 + math.pi/6),  # Sol kol hafif önde
    "right_leg": (8, 40, math.pi/2 + math.pi/6),  # Sağ bacak hafif önde
    "left_leg": (-8, 40, math.pi/2 - math.pi/6)  # Sol bacak hafif arkada
})

# Orta poz
walk.add_keyframe(0.3, {
    "body": (0, -4, -math.pi/2),  # Gövde hafif yukarı
    "head": (0, 0, math.pi/12),  # Kafa hafif yana
    "right_arm": (8, -8, math.pi/2 + math.pi/4),  # Sağ kol önde
    "left_arm": (-8, -8, math.pi/2 - math.pi/4),  # Sol kol arkada
    "right_leg": (8, 40, math.pi/2 - math.pi/4),  # Sağ bacak arkada
    "left_leg": (-8, 40, math.pi/2 + math.pi/4)  # Sol bacak önde
})

# Son poz (başlangıç pozunun aynası)
walk.add_keyframe(0.6, {
    "body": (0, 0, -math.pi/2),  # Gövde dikey
    "head": (0, 0, 0),  # Kafa düz
    "right_arm": (8, -8, math.pi/2 + math.pi/6),  # Sağ kol hafif önde
    "left_arm": (-8, -8, math.pi/2 - math.pi/6),  # Sol kol hafif arkada
    "right_leg": (8, 40, math.pi/2 - math.pi/6),  # Sağ bacak hafif arkada
    "left_leg": (-8, 40, math.pi/2 + math.pi/6)  # Sol bacak hafif önde
})

# Animasyonu iskelet sistemine ekle ve başlat
skeleton.add_animation(walk)
skeleton.play_animation("walk", loop=True)

# Font başlat
font = pygame.font.Font(None, 36)

# Ana döngü
running = True
debug_mode = False
while running:
    # FPS'i sabitle
    dt = clock.tick(FPS) / 1000.0  # Delta time'ı saniye cinsinden al
    
    # Olayları işle
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                debug_mode = not debug_mode  # Debug modu aç/kapa
    
    # İskeleti güncelle
    skeleton.update(dt)
    
    # Çizim
    screen.fill((255, 255, 255))  # Beyaz arkaplan
    skeleton.draw(screen, (400, 300), debug=debug_mode)  # İskeleti çiz
    
    # FPS göster
    fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))
    
    # Ekranı güncelle
    pygame.display.flip()

# Pygame'i kapat
pygame.quit()
sys.exit() 