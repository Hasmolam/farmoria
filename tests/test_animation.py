import pytest
import pygame
import math
from engine.animation import Skeleton, Animation, Bone

@pytest.fixture
def skeleton():
    """Test için basit bir iskelet oluştur"""
    skel = Skeleton()
    
    # Gövde kemiği
    skel.add_bone("body", length=50.0)
    
    # Sağ kol kemikleri
    skel.add_bone("right_upper_arm", length=30.0, parent_name="body", 
                 angle=math.pi/4, position=(40, 0))
    skel.add_bone("right_lower_arm", length=25.0, parent_name="right_upper_arm",
                 angle=math.pi/4)
    
    # Sol kol kemikleri
    skel.add_bone("left_upper_arm", length=30.0, parent_name="body",
                 angle=-math.pi/4, position=(-40, 0))
    skel.add_bone("left_lower_arm", length=25.0, parent_name="left_upper_arm",
                 angle=-math.pi/4)
    
    # Bacak kemikleri
    skel.add_bone("right_leg", length=40.0, parent_name="body",
                 angle=math.pi/6, position=(20, 45))
    skel.add_bone("left_leg", length=40.0, parent_name="body",
                 angle=-math.pi/6, position=(-20, 45))
    
    return skel

@pytest.fixture
def walk_animation():
    """Yürüme animasyonu oluştur"""
    anim = Animation("walk", duration=1.0)
    
    # Başlangıç pozu (t=0.0)
    anim.add_keyframe(0.0, {
        "body": (0, 0, 0),
        "right_upper_arm": (40, 0, math.pi/4),
        "right_lower_arm": (0, 0, math.pi/4),
        "left_upper_arm": (-40, 0, -math.pi/4),
        "left_lower_arm": (0, 0, -math.pi/4),
        "right_leg": (20, 45, math.pi/6),
        "left_leg": (-20, 45, -math.pi/6)
    })
    
    # Orta poz (t=0.5)
    anim.add_keyframe(0.5, {
        "body": (0, -5, 0),  # Zıplama
        "right_upper_arm": (40, 0, -math.pi/4),  # Kollar ters sallanır
        "right_lower_arm": (0, 0, -math.pi/6),
        "left_upper_arm": (-40, 0, math.pi/4),
        "left_lower_arm": (0, 0, math.pi/6),
        "right_leg": (20, 45, -math.pi/6),  # Bacaklar ters sallanır
        "left_leg": (-20, 45, math.pi/6)
    })
    
    # Bitiş pozu (t=1.0) - Başlangıç pozuna dön
    anim.add_keyframe(1.0, {
        "body": (0, 0, 0),
        "right_upper_arm": (40, 0, math.pi/4),
        "right_lower_arm": (0, 0, math.pi/4),
        "left_upper_arm": (-40, 0, -math.pi/4),
        "left_lower_arm": (0, 0, -math.pi/4),
        "right_leg": (20, 45, math.pi/6),
        "left_leg": (-20, 45, -math.pi/6)
    })
    
    return anim

def test_bone_creation(skeleton):
    """Kemik oluşturma ve hiyerarşiyi test et"""
    # Kemik sayısını kontrol et
    assert len(skeleton.bones) == 7
    
    # Kök kemik sayısını kontrol et
    assert len(skeleton.root_bones) == 1
    
    # Kemik hiyerarşisini kontrol et
    body = skeleton.bones["body"]
    right_upper_arm = skeleton.bones["right_upper_arm"]
    right_lower_arm = skeleton.bones["right_lower_arm"]
    
    assert right_upper_arm.parent == body
    assert right_lower_arm.parent == right_upper_arm
    assert right_upper_arm in body.children
    assert right_lower_arm in right_upper_arm.children

def test_bone_transformations(skeleton):
    """Kemik dönüşümlerini test et"""
    right_upper_arm = skeleton.bones["right_upper_arm"]
    
    # Dünya matrisini kontrol et
    world_matrix = right_upper_arm.get_world_matrix()
    assert world_matrix.shape == (3, 3)
    
    # Uç noktası pozisyonunu kontrol et
    tip_x, tip_y = right_upper_arm.get_tip_position()
    assert isinstance(tip_x, float)
    assert isinstance(tip_y, float)

def test_animation_keyframes(walk_animation):
    """Animasyon karelerini test et"""
    # Kare sayısını kontrol et
    assert len(walk_animation.keyframes) == 3
    
    # Karelerin zamanlarını kontrol et
    assert walk_animation.keyframes[0].time == 0.0
    assert walk_animation.keyframes[1].time == 0.5
    assert walk_animation.keyframes[2].time == 1.0
    
    # Kare içeriğini kontrol et
    first_frame = walk_animation.keyframes[0]
    assert len(first_frame.bone_poses) == 7
    assert "body" in first_frame.bone_poses
    assert "right_upper_arm" in first_frame.bone_poses

def test_animation_interpolation(walk_animation):
    """Animasyon interpolasyonunu test et"""
    # t=0.25 anındaki pozu al (ilk iki kare arası)
    pose_025 = walk_animation.get_pose_at_time(0.25)
    assert len(pose_025) == 7
    
    # Vücut yüksekliğinin interpolasyonunu kontrol et
    body_pos = pose_025["body"]
    assert body_pos[1] == -2.5  # -5 * 0.5 interpolasyon
    
    # t=0.75 anındaki pozu al (son iki kare arası)
    pose_075 = walk_animation.get_pose_at_time(0.75)
    assert len(pose_075) == 7

def test_animation_playback(skeleton, walk_animation):
    """Animasyon oynatmayı test et"""
    # Animasyonu iskelet sistemine ekle
    skeleton.add_animation(walk_animation)
    
    # Animasyonu başlat
    skeleton.play_animation("walk")
    assert skeleton.current_animation == walk_animation
    assert skeleton.current_animation.is_playing
    
    # Animasyonu güncelle
    skeleton.update(0.1)  # 0.1 saniye ilerlet
    assert skeleton.current_animation.current_time == 0.1
    
    # Animasyonu duraklat
    skeleton.current_animation.pause()
    assert not skeleton.current_animation.is_playing
    
    # Animasyonu devam ettir
    skeleton.current_animation.play()
    assert skeleton.current_animation.is_playing

def test_skeleton_drawing(skeleton):
    """İskelet çizimini test et"""
    # Test yüzeyi oluştur
    surface = pygame.Surface((400, 400))
    
    # Normal çizim
    skeleton.draw(surface, (200, 200))
    
    # Debug modunda çizim
    skeleton.draw(surface, (200, 200), debug=True)

def test_skeleton_serialization(skeleton, walk_animation, tmp_path):
    """İskelet ve animasyon kaydetme/yükleme işlemlerini test et"""
    # Animasyonu ekle
    skeleton.add_animation(walk_animation)
    
    # Dosyaya kaydet
    save_path = tmp_path / "test_skeleton.json"
    skeleton.save_to_file(str(save_path))
    
    # Dosyadan yükle
    loaded_skeleton = Skeleton.load_from_file(str(save_path))
    
    # Kemik sayısını kontrol et
    assert len(loaded_skeleton.bones) == len(skeleton.bones)
    
    # Animasyon sayısını kontrol et
    assert len(loaded_skeleton.animations) == len(skeleton.animations)
    
    # İlk animasyonun kare sayısını kontrol et
    loaded_anim = loaded_skeleton.animations["walk"]
    assert len(loaded_anim.keyframes) == len(walk_animation.keyframes) 