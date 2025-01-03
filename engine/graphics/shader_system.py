import moderngl
import pygame
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import os
from .debug import debug_manager, DebugCategory, DebugLevel

@dataclass
class ShaderProgram:
    """Shader programını temsil eden sınıf"""
    program: moderngl.Program
    vertex_shader: str
    fragment_shader: str
    name: str
    uniforms: Dict[str, any] = None

    def __post_init__(self):
        if self.uniforms is None:
            self.uniforms = {}

class ShaderSystem:
    """2D shader sistemini yöneten sınıf"""
    def __init__(self, width: int, height: int):
        # ModernGL bağlamı oluştur
        self.ctx = moderngl.create_standalone_context()
        self.width = width
        self.height = height
        
        # Temel quad mesh oluştur (2D için)
        self.quad_buffer = self.ctx.buffer(
            np.array([
                # pozisyon (x, y), texture koordinatları (u, v)
                -1.0, -1.0, 0.0, 0.0,  # sol alt
                 1.0, -1.0, 1.0, 0.0,  # sağ alt
                -1.0,  1.0, 0.0, 1.0,  # sol üst
                 1.0,  1.0, 1.0, 1.0,  # sağ üst
            ], dtype='f4').tobytes()
        )
        
        # Vertex Array Object oluştur
        self.quad_vao = self.ctx.vertex_array(
            self.ctx.program(
                vertex_shader=self.load_shader('default.vert'),
                fragment_shader=self.load_shader('default.frag')
            ),
            [(self.quad_buffer, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # Framebuffer ve texture oluştur
        self.fbo_texture = self.ctx.texture((width, height), 4)
        self.fbo = self.ctx.framebuffer(self.fbo_texture)
        
        # Shader programları
        self.shader_programs: Dict[str, ShaderProgram] = {}
        self.current_program: Optional[ShaderProgram] = None
        
        # Varsayılan shaderları yükle
        self.load_default_shaders()
        
        debug_manager.log(
            "Shader System başlatıldı",
            DebugCategory.SHADER,
            DebugLevel.INFO,
            {"width": width, "height": height}
        )
    
    def load_shader(self, filename: str) -> str:
        """Shader dosyasını yükle"""
        shader_dir = os.path.join(os.path.dirname(__file__), 'shaders')
        with open(os.path.join(shader_dir, filename), 'r') as f:
            return f.read()
    
    def load_default_shaders(self):
        """Varsayılan shaderları yükle"""
        # Basit renk shader'ı
        self.create_shader_program(
            'color',
            self.load_shader('color.vert'),
            self.load_shader('color.frag')
        )
        
        # Işıklandırma shader'ı
        self.create_shader_program(
            'lighting',
            self.load_shader('lighting.vert'),
            self.load_shader('lighting.frag')
        )
        
        # Blur shader'ı
        self.create_shader_program(
            'blur',
            self.load_shader('blur.vert'),
            self.load_shader('blur.frag')
        )
    
    def create_shader_program(self, name: str, vertex_shader: str, fragment_shader: str) -> ShaderProgram:
        """Yeni bir shader programı oluştur"""
        debug_manager.start_performance_metric(f"create_shader_{name}")
        try:
            program = self.ctx.program(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader
            )
            shader_program = ShaderProgram(program, vertex_shader, fragment_shader, name)
            self.shader_programs[name] = shader_program
            
            debug_manager.log(
                f"Shader programı oluşturuldu: {name}",
                DebugCategory.SHADER,
                DebugLevel.INFO
            )
            
            return shader_program
        except Exception as e:
            debug_manager.log(
                f"Shader derleme hatası: {name}",
                DebugCategory.SHADER,
                DebugLevel.ERROR,
                {"error": str(e)}
            )
            raise
        finally:
            debug_manager.end_performance_metric(f"create_shader_{name}")
    
    def use_shader(self, name: str):
        """Belirtilen shader programını kullan"""
        if name in self.shader_programs:
            self.current_program = self.shader_programs[name]
    
    def set_uniform(self, name: str, value: any):
        """Shader uniform değişkenini ayarla"""
        if self.current_program:
            self.current_program.uniforms[name] = value
            if name in self.current_program.program:
                uniform = self.current_program.program[name]
                
                # Uniform tipine göre değeri ayarla
                if isinstance(value, (int, float)):
                    uniform.value = value
                elif isinstance(value, (tuple, list)) and len(value) in [2, 3, 4]:
                    uniform.value = tuple(value)
                elif isinstance(value, moderngl.Texture):
                    uniform.value = value
    
    def render_to_texture(self, surface: pygame.Surface) -> pygame.Surface:
        """Pygame surface'ini shader ile işle ve yeni surface döndür"""
        debug_manager.start_performance_metric("render_to_texture")
        try:
            # Surface'i texture'a dönüştür
            texture_data = pygame.image.tostring(surface, 'RGBA', True)
            input_texture = self.ctx.texture(surface.get_size(), 4, texture_data)
            
            # Framebuffer'a bağlan
            self.fbo.use()
            
            # Viewport ayarla
            self.ctx.viewport = (0, 0, self.width, self.height)
            
            # Ekranı temizle
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)
            
            # Input texture'ı bağla
            input_texture.use(0)
            
            if self.current_program:
                debug_manager.log(
                    f"Shader uygulanıyor: {self.current_program.name}",
                    DebugCategory.SHADER,
                    DebugLevel.DEBUG,
                    {"uniforms": list(self.current_program.uniforms.keys())}
                )
                
                # Shader programını kullan
                self.current_program.program['texture0'].value = 0
                
                # Uniform değişkenleri ayarla
                for name, value in self.current_program.uniforms.items():
                    self.set_uniform(name, value)
            
            # Quad'ı çiz
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)
            
            # Framebuffer'dan veriyi oku
            buffer = self.fbo.read(components=4)
            
            # Yeni pygame surface oluştur
            output_surface = pygame.image.fromstring(
                buffer, (self.width, self.height), 'RGBA'
            )
            
            return output_surface
        except Exception as e:
            debug_manager.log(
                "Render hatası",
                DebugCategory.SHADER,
                DebugLevel.ERROR,
                {"error": str(e)}
            )
            raise
        finally:
            # Kaynakları temizle
            input_texture.release()
            debug_manager.end_performance_metric("render_to_texture")
    
    def draw_debug_overlay(self, surface: pygame.Surface):
        """Debug bilgilerini çiz."""
        if not debug_manager.enabled:
            return
            
        font = pygame.font.Font(None, 20)
        y = 10
        
        # Aktif shader bilgisi
        if self.current_program:
            shader_text = f"Aktif Shader: {self.current_program.name}"
            text_surface = font.render(shader_text, True, (0, 255, 0))
            surface.blit(text_surface, (10, y))
            y += 20
            
            # Uniform değişkenler
            for name, value in self.current_program.uniforms.items():
                uniform_text = f"Uniform {name}: {value}"
                text_surface = font.render(uniform_text, True, (0, 255, 0))
                surface.blit(text_surface, (10, y))
                y += 20
        
        # Performans metrikleri
        stats = self.get_performance_stats()
        stats_text = f"FPS: {stats['fps']:.1f} | Draw Calls: {stats['draw_calls']}"
        text_surface = font.render(stats_text, True, (0, 255, 0))
        surface.blit(text_surface, (10, y))
    
    def get_performance_stats(self) -> dict:
        """Performans istatistiklerini döndür."""
        return {
            "fps": debug_manager.get_fps(),
            "draw_calls": self._draw_calls,
            "active_textures": len(self._active_textures),
            "shader_switches": self._shader_switches,
            "total_shaders": len(self.shader_programs)
        }
    
    def cleanup(self):
        """Shader sistemini temizle"""
        debug_manager.log(
            "Shader System kaynakları temizleniyor",
            DebugCategory.SHADER,
            DebugLevel.INFO
        )
        
        self.quad_buffer.release()
        self.quad_vao.release()
        self.fbo_texture.release()
        self.fbo.release()
        
        for program in self.shader_programs.values():
            program.program.release()
            
        self.ctx.release() 