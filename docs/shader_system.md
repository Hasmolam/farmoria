# Shader System

Shader System, ModernGL kullanarak 2D oyunlar için güçlü bir grafik işleme sistemi sunar. Özelleştirilebilir shader'lar, post-processing efektleri ve performans optimizasyonları içerir.

## Temel Bileşenler

### ShaderProgram

```python
program = ShaderProgram(
    vertex_shader=vertex_code,
    fragment_shader=fragment_code
)
```

#### Özellikler
- `program`: ModernGL program nesnesi
- `vertex_shader`: Vertex shader kodu
- `fragment_shader`: Fragment shader kodu
- `uniforms`: Uniform değişkenler

### ShaderSystem

```python
shader_system = ShaderSystem(width=800, height=600)
```

#### Özellikler
- `ctx`: ModernGL bağlamı
- `width`: Render genişliği
- `height`: Render yüksekliği
- `shader_programs`: Shader program koleksiyonu
- `current_program`: Aktif shader program

## Varsayılan Shaderlar

### Color Shader

```glsl
// color.vert
#version 330
in vec2 in_position;
in vec2 in_texcoord;
out vec2 v_texcoord;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    v_texcoord = in_texcoord;
}

// color.frag
#version 330
uniform sampler2D texture0;
uniform vec4 color;
in vec2 v_texcoord;
out vec4 f_color;

void main() {
    f_color = texture(texture0, v_texcoord) * color;
}
```

### Lighting Shader

```glsl
// lighting.frag
#version 330
uniform sampler2D texture0;
uniform vec2 light_pos;
uniform vec3 light_color;
uniform float light_radius;
in vec2 v_texcoord;
out vec4 f_color;

void main() {
    vec4 color = texture(texture0, v_texcoord);
    float distance = length(light_pos - gl_FragCoord.xy);
    float attenuation = 1.0 - smoothstep(0.0, light_radius, distance);
    f_color = color * vec4(light_color * attenuation, 1.0);
}
```

### Blur Shader

```glsl
// blur.frag
#version 330
uniform sampler2D texture0;
uniform vec2 resolution;
uniform float blur_radius;
in vec2 v_texcoord;
out vec4 f_color;

void main() {
    vec4 color = vec4(0.0);
    vec2 texel = 1.0 / resolution;
    
    for(float x = -blur_radius; x <= blur_radius; x++) {
        for(float y = -blur_radius; y <= blur_radius; y++) {
            vec2 offset = vec2(x, y) * texel;
            color += texture(texture0, v_texcoord + offset);
        }
    }
    
    color /= pow(blur_radius * 2.0 + 1.0, 2.0);
    f_color = color;
}
```

## Temel Kullanım

### Shader Programı Oluşturma

```python
# Shader kodlarını yükle
vertex_code = shader_system.load_shader('custom.vert')
fragment_code = shader_system.load_shader('custom.frag')

# Program oluştur
program = shader_system.create_shader_program(
    'custom',
    vertex_code,
    fragment_code
)
```

### Shader Kullanma

```python
# Shader'ı aktifleştir
shader_system.use_shader('custom')

# Uniform değişkenleri ayarla
shader_system.set_uniform('color', (1.0, 0.0, 0.0, 1.0))
shader_system.set_uniform('scale', 2.0)

# Surface'i işle
processed_surface = shader_system.render_to_texture(game_surface)
```

## Post-Processing Efektleri

### Blur Efekti

```python
# Blur shader'ı kullan
shader_system.use_shader('blur')
shader_system.set_uniform('blur_radius', 5.0)
shader_system.set_uniform('resolution', (800, 600))

# Efekti uygula
blurred = shader_system.render_to_texture(screen)
```

### Işık Efekti

```python
# Işık shader'ı kullan
shader_system.use_shader('lighting')
shader_system.set_uniform('light_pos', (400, 300))
shader_system.set_uniform('light_color', (1.0, 0.8, 0.6))
shader_system.set_uniform('light_radius', 200.0)

# Efekti uygula
lit_surface = shader_system.render_to_texture(screen)
```

## Performans Optimizasyonu

1. Shader Derleme
   - Shader'ları önceden derleyin
   - Hata kontrolü yapın
   - Shader önbelleği kullanın

2. Uniform Yönetimi
   - Uniform değerlerini önbellekleyin
   - Gereksiz uniform güncellemelerinden kaçının
   - Uniform buffer nesneleri kullanın

3. Render Hedefleri
   - Framebuffer'ları yeniden kullanın
   - Texture boyutlarını optimize edin
   - Mipmap kullanımını değerlendirin

## Hata Ayıklama

```python
# Shader derleme hatalarını kontrol et
try:
    program = shader_system.create_shader_program('test', vert, frag)
except Exception as e:
    print(f"Shader derleme hatası: {e}")

# Performans metrikleri
stats = shader_system.get_performance_stats()
print(f"FPS: {stats['fps']}")
print(f"Draw calls: {stats['draw_calls']}")
```

## En İyi Uygulamalar

1. Shader Geliştirme
   - GLSL sürümünü kontrol edin
   - Platform uyumluluğunu test edin
   - Shader kodunu modüler tutun

2. Performans
   - Kompleks matematik işlemlerini optimize edin
   - Koşul ifadelerini minimize edin
   - Texture erişimlerini optimize edin

3. Bellek Yönetimi
   - Kaynakları düzgün temizleyin
   - Texture boyutlarını kontrol edin
   - Vertex buffer'ları yeniden kullanın 