import pytest
import pygame
import moderngl
import numpy as np
from engine.graphics.shader_system import ShaderSystem, ShaderProgram

@pytest.fixture
def shader_system():
    pygame.init()
    system = ShaderSystem(800, 600)
    yield system
    system.cleanup()
    pygame.quit()

def test_initialization(shader_system):
    """Test shader system initialization"""
    assert shader_system.width == 800
    assert shader_system.height == 600
    assert isinstance(shader_system.ctx, moderngl.Context)
    assert shader_system.quad_buffer is not None
    assert shader_system.quad_vao is not None
    assert shader_system.fbo_texture is not None
    assert shader_system.fbo is not None

def test_shader_program_creation():
    """Test ShaderProgram dataclass"""
    program = moderngl.create_standalone_context().program(
        vertex_shader="""
            #version 330
            in vec2 in_position;
            void main() {
                gl_Position = vec4(in_position, 0.0, 1.0);
            }
        """,
        fragment_shader="""
            #version 330
            out vec4 fragColor;
            void main() {
                fragColor = vec4(1.0);
            }
        """
    )
    shader_program = ShaderProgram(
        program=program,
        vertex_shader="vertex_source",
        fragment_shader="fragment_source",
        name="test_shader"
    )
    assert shader_program.name == "test_shader"
    assert shader_program.uniforms == {}

def test_load_default_shaders(shader_system):
    """Test loading default shaders"""
    assert 'color' in shader_system.shader_programs
    assert 'lighting' in shader_system.shader_programs
    assert 'blur' in shader_system.shader_programs

def test_use_shader(shader_system):
    """Test shader selection"""
    shader_system.use_shader('color')
    assert shader_system.current_program == shader_system.shader_programs['color']
    
    # Test invalid shader selection
    shader_system.use_shader('nonexistent')
    assert shader_system.current_program == shader_system.shader_programs['color']

def test_set_uniform(shader_system):
    """Test setting uniform values"""
    shader_system.use_shader('color')
    
    # Test scalar uniform
    shader_system.set_uniform('intensity', 0.5)
    assert shader_system.current_program.uniforms['intensity'] == 0.5
    
    # Test vector uniform
    shader_system.set_uniform('color', (1.0, 0.0, 0.0))
    assert shader_system.current_program.uniforms['color'] == (1.0, 0.0, 0.0)

def test_render_to_texture(shader_system):
    """Test rendering with shader"""
    # Create test surface
    surface = pygame.Surface((100, 100))
    surface.fill((255, 0, 0))  # Red surface
    
    # Use color shader
    shader_system.use_shader('color')
    shader_system.set_uniform('intensity', 1.0)
    
    # Render
    result = shader_system.render_to_texture(surface)
    assert isinstance(result, pygame.Surface)
    assert result.get_size() == (800, 600)

def test_cleanup(shader_system):
    """Test cleanup process"""
    shader_system.cleanup()
    # Verify that cleanup doesn't raise any exceptions 