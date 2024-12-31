import pytest
import pymunk
from engine.systems.physics import PhysicsSystem, PhysicsBody

@pytest.fixture
def physics_system():
    """Test için fizik sistemi oluşturur"""
    return PhysicsSystem()

@pytest.fixture
def physics_body():
    """Test için fizik gövdesi oluşturur"""
    return PhysicsBody()

class TestPhysicsBody:
    def test_initialization(self, physics_body):
        """Fizik gövdesinin doğru başlatıldığını kontrol eder"""
        assert isinstance(physics_body.body, pymunk.Body)
        assert len(physics_body.shapes) == 0
        assert physics_body.body.body_type == pymunk.Body.DYNAMIC

    def test_static_body(self):
        """Statik gövde oluşturmayı test eder"""
        body = PhysicsBody(body_type="static")
        assert body.body.body_type == pymunk.Body.STATIC

    def test_kinematic_body(self):
        """Kinematik gövde oluşturmayı test eder"""
        body = PhysicsBody(body_type="kinematic")
        assert body.body.body_type == pymunk.Body.KINEMATIC

    def test_add_circle_shape(self, physics_body):
        """Daire şekli eklemeyi test eder"""
        physics_body.add_circle_shape(radius=10)
        assert len(physics_body.shapes) == 1
        assert isinstance(physics_body.shapes[0], pymunk.Circle)

    def test_add_box_shape(self, physics_body):
        """Kutu şekli eklemeyi test eder"""
        physics_body.add_box_shape(width=20, height=30)
        assert len(physics_body.shapes) == 1
        assert isinstance(physics_body.shapes[0], pymunk.Poly)

    def test_position(self, physics_body):
        """Pozisyon özelliğini test eder"""
        physics_body.position = (100, 200)
        assert physics_body.position == (100, 200)

    def test_angle(self, physics_body):
        """Açı özelliğini test eder"""
        physics_body.angle = 1.5
        assert physics_body.angle == 1.5

    def test_apply_force(self, physics_body):
        """Kuvvet uygulamayı test eder"""
        # Önce bir space oluştur ve gövdeyi ekle
        space = pymunk.Space()
        space.add(physics_body.body)
        
        # Varsayılan şekil ekle
        shape = physics_body.add_box_shape(10, 10)
        space.add(shape)
        
        # Kuvvet uygula
        physics_body.apply_force((1000, 0))
        
        # Simülasyonu güncelle
        space.step(1/60.0)
        
        # Hız değişmiş olmalı
        assert physics_body.body.velocity.x > 0

    def test_apply_impulse(self, physics_body):
        """Impuls uygulamayı test eder"""
        initial_velocity = physics_body.body.velocity
        physics_body.apply_impulse((100, 0))
        assert physics_body.body.velocity != initial_velocity

class TestPhysicsSystem:
    def test_initialization(self, physics_system):
        """Fizik sisteminin doğru başlatıldığını kontrol eder"""
        assert isinstance(physics_system.space, pymunk.Space)
        assert len(physics_system.bodies) == 0

    def test_create_body(self, physics_system):
        """Gövde oluşturmayı test eder"""
        body = physics_system.create_body("test_body")
        assert "test_body" in physics_system.bodies
        assert isinstance(physics_system.bodies["test_body"], PhysicsBody)

    def test_remove_body(self, physics_system):
        """Gövde kaldırmayı test eder"""
        physics_system.create_body("test_body")
        physics_system.remove_body("test_body")
        assert "test_body" not in physics_system.bodies

    def test_get_body(self, physics_system):
        """Gövde almayı test eder"""
        physics_system.create_body("test_body")
        body = physics_system.get_body("test_body")
        assert isinstance(body, PhysicsBody)
        assert physics_system.get_body("nonexistent") is None

    def test_gravity(self, physics_system):
        """Yerçekimi ayarlamayı test eder"""
        physics_system.set_gravity(0, -981)  # 9.81 m/s^2
        assert physics_system.space.gravity == (0, -981)

    def test_update(self, physics_system):
        """Fizik güncellemesini test eder"""
        body = physics_system.create_body("test_body")
        body.position = (0, 0)
        physics_system.set_gravity(0, -981)
        
        # Bir süre güncelle
        physics_system.update(0.1)
        # Yerçekimi etkisiyle y pozisyonu değişmeli
        assert body.position[1] < 0

    def test_collision_handler(self, physics_system):
        """Çarpışma yönetimini test eder"""
        def on_collision(arbiter, space, data):
            return True
            
        handler = physics_system.add_collision_handler(1, 2)
        handler.begin = on_collision
        
        # İki cisim oluştur ve çarpıştır
        body1 = physics_system.create_body("body1")
        body2 = physics_system.create_body("body2")
        
        body1.add_circle_shape(10)
        body2.add_circle_shape(10)
        
        body1.shapes[0].collision_type = 1
        body2.shapes[0].collision_type = 2
        
        # Cisimleri çarpışacak şekilde konumlandır
        body1.position = (0, 0)
        body2.position = (15, 0)  # Yarıçaplar toplamından az mesafe
        
        physics_system.update(0.1)  # Çarpışma kontrolü için güncelle 