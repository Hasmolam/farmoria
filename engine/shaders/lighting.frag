#version 330

uniform sampler2D texture0;
uniform vec2 light_position;
uniform float light_radius;
uniform vec3 light_color;
uniform float ambient_strength;

in vec2 v_texcoord;
in vec2 v_position;
out vec4 f_color;

void main() {
    // Temel texture rengi
    vec4 tex_color = texture(texture0, v_texcoord);
    
    // Piksel pozisyonunu hesapla
    vec2 pixel_pos = (v_position + 1.0) * 0.5;
    
    // Işık kaynağına olan uzaklığı hesapla
    float distance = length(pixel_pos - light_position);
    
    // Işık şiddetini hesapla
    float attenuation = 1.0 - smoothstep(0.0, light_radius, distance);
    
    // Ambient ışık
    vec3 ambient = ambient_strength * vec3(1.0);
    
    // Diffuse ışık
    vec3 diffuse = attenuation * light_color;
    
    // Son rengi hesapla
    vec3 lighting = ambient + diffuse;
    f_color = vec4(tex_color.rgb * lighting, tex_color.a);
} 