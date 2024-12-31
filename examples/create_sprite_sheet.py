import pygame
import os

# Pygame başlat
pygame.init()

# Sprite sheet boyutları
SHEET_WIDTH = 256  # Daha geniş bir sprite sheet
SHEET_HEIGHT = 256  # Daha yüksek bir sprite sheet

# Sprite sheet yüzeyi oluştur
sprite_sheet = pygame.Surface((SHEET_WIDTH, SHEET_HEIGHT), pygame.SRCALPHA)

# Vücut parçalarının boyutları
BODY_WIDTH = 32
BODY_HEIGHT = 48
HEAD_SIZE = 24
LIMB_WIDTH = 16
LIMB_HEIGHT = 32

# Vücut (gövde) - kırmızı
body = pygame.Surface((BODY_WIDTH, BODY_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(body, (255, 0, 0, 255), (8, 0, 16, BODY_HEIGHT))  # Daha belirgin gövde
sprite_sheet.blit(body, (0, 0))

# Kafa - sarı
head = pygame.Surface((HEAD_SIZE, HEAD_SIZE), pygame.SRCALPHA)
pygame.draw.circle(head, (255, 255, 0, 255), (HEAD_SIZE//2, HEAD_SIZE//2), HEAD_SIZE//2-2)  # Daha belirgin kafa
sprite_sheet.blit(head, (BODY_WIDTH + 8, 0))

# Sağ kol - mavi
right_arm = pygame.Surface((LIMB_WIDTH, LIMB_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(right_arm, (0, 0, 255, 255), (4, 0, 8, LIMB_HEIGHT))  # Daha belirgin kol
sprite_sheet.blit(right_arm, (BODY_WIDTH + HEAD_SIZE + 16, 0))

# Sol kol - açık mavi
left_arm = pygame.Surface((LIMB_WIDTH, LIMB_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(left_arm, (0, 128, 255, 255), (4, 0, 8, LIMB_HEIGHT))  # Daha belirgin kol
sprite_sheet.blit(left_arm, (BODY_WIDTH + HEAD_SIZE + LIMB_WIDTH + 24, 0))

# Sağ bacak - yeşil
right_leg = pygame.Surface((LIMB_WIDTH, LIMB_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(right_leg, (0, 255, 0, 255), (4, 0, 8, LIMB_HEIGHT))  # Daha belirgin bacak
sprite_sheet.blit(right_leg, (BODY_WIDTH + HEAD_SIZE + LIMB_WIDTH * 2 + 32, 0))

# Sol bacak - açık yeşil
left_leg = pygame.Surface((LIMB_WIDTH, LIMB_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(left_leg, (128, 255, 0, 255), (4, 0, 8, LIMB_HEIGHT))  # Daha belirgin bacak
sprite_sheet.blit(left_leg, (BODY_WIDTH + HEAD_SIZE + LIMB_WIDTH * 3 + 40, 0))

# Sprite sheet'i kaydet
pygame.image.save(sprite_sheet, os.path.join("assets", "character_sheet.png"))

print("Sprite sheet başarıyla oluşturuldu: assets/character_sheet.png")
pygame.quit() 